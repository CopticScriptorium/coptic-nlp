#!/usr/bin/python
#  -*- coding: utf-8 -*-


from __future__ import unicode_literals
import sys, re, io
PY3 = sys.version_info[0] == 3

cap_map = {"Ⲁ":"ⲁ","Ⲃ":"ⲃ","Ⲑ":"ⲑ","Ⲇ":"ⲇ","Ⲉ":"ⲉ","Ϥ":"ϥ","Ⲅ":"ⲅ","Ⲏ":"ⲏ","Ⲓ":"ⲓ","Ϫ":"ϫ","Ⲕ":"ⲕ","Ⲗ":"ⲗ","Ⲙ":"ⲙ","Ⲛ":"ⲛ","Ⲟ":"ⲟ","Ⲡ":"ⲡ","Ϭ":"ϭ","Ⲣ":"ⲣ","Ⲥ":"ⲥ","Ⲧ":"ⲧ","Ⲩ":"ⲩ","Ⲫ":"ⲫ","Ⲱ":"ⲱ","Ϩ":"ϩ","Ⲭ":"ⲭ","Ⲍ":"ⲍ","Ϣ":"ϣ","Ϯ":"ϯ","Ⲯ":"ⲯ","Ⲝ":"ⲝ"}

if PY3 and __name__ != "__main__":
	from .tokenize_fs import fs_tokenize
	from .tokenize_lookup import lookup_tokenize
	from .tokenize_rf import RFTokenizer
	from .tokenize_morph import MorphAnalyzer
	from .tokenize_rf import MultiColumnLabelEncoder, lambda_underscore, DataFrameSelector
else:
	from tokenize_fs import fs_tokenize
	from tokenize_lookup import lookup_tokenize
	from tokenize_rf import RFTokenizer
	from tokenize_morph import MorphAnalyzer
	from tokenize_rf import MultiColumnLabelEncoder, lambda_underscore, DataFrameSelector

from argparse import ArgumentParser
from six import iteritems

if not PY3:
	reload(sys)
	sys.setdefaultencoding('utf8')
	from itertools import izip as zip

sys.path.append("lib")

class BoundGroup():

	# Static list of characters that are removed from norm text (basic normalization)
	orig_chars = ["̈", "", "̄", "̀", "̣", "`", "̅", "̈", "̂", "︤", "︥", "︦", "⳿", "~", "\n", "[", "]", "̇", "᷍"]
	tokenization_chars = ["|", "-"]

	def __init__(self, out_tok_sep="|"):
		self.dirty = ""
		self.norm = ""
		self.orig = ""
		self.tokenization = ""  # Holds the clean tokenization (a|f|sOtm)
		self.tokenized = ""  # Holds the dirty tokenization (a^|f|sO<hi rend="x">t</hi>m)
		self.unaligned_tokenization = ""  # Holds irregular, unalignable tokenization only be expressible in SGML (n|t|he)
		self.pretokenization = ""  # Holds pre-specified tokenization (pipes in input)
		self.cursor = 0
		self.norm_cursor = 0
		self.mode = "text"
		self.norm_map = {}  # Dictionary from clean character position to dirty position, without seps
		self.out_tok_sep = out_tok_sep  # Separator to print between subtokens in 'pipes' mode

	# Add a character to the bound group
	def affix(self, c, tokenized=False):

		if c == "|": # Input to ML tokenizer can't contain '|' or '-'
			if tokenized and self.mode!="xml":
				self.pretokenization += c
				return None
			else:
				c = "□"
		elif c == "-":
			if tokenized and self.mode!="xml":
				self.pretokenization += c
				return None
			else:
				c = "■"

		self.dirty += c

		if c == "<":
			self.mode = "xml"

		if self.mode != "xml":
			if c in self.orig_chars:
				self.orig += c
				self.norm_map[self.norm_cursor] = self.cursor
			else:
				self.orig += c
				if c == "⳯":  # ad-hoc normalization of superscript ni chracter
					c = "ⲛ"
				elif c in cap_map:
					c = cap_map[c]
				self.norm += c
				if c not in ["□","■"] and tokenized:
					self.pretokenization += c
				self.norm_map[self.norm_cursor] = self.cursor
				self.norm_cursor += 1

		if c == ">":
			self.mode = "text"

		self.cursor += 1

	def add_tokenization(self, tokenization):
		# Retain real tokenization for SGML output
		self.tokenization = tokenization
		# Construct approximate tokenization for piped output
		len_offset = 0
		if "ⲑ" in self.dirty and ("ⲧ|ϩ" in tokenization or "ⲧ-ϩ" in tokenization):
			tokenization = tokenization.replace("ⲧ|ϩ","ⲑ|").replace("ⲧ-ϩ","ⲑ-")
		if "ϯ" in self.dirty and "ⲧ|ⲓ" in tokenization:
			tokenization = tokenization.replace("ⲧ|ⲓ","|ϯ")
		if "ⲉⲧⲛⲁ" in self.dirty and "ⲉⲧⲛ|ⲛⲁ" in tokenization and "ⲉⲧⲛⲛⲁ" not in self.dirty:
			tokenization = tokenization.replace("ⲉⲧⲛ|ⲛⲁ","ⲉⲧⲛ|ⲁ")
		tokenized = self.dirty
		tok_rep = tokenization.replace("|","").replace("-","").strip()
		if len(self.norm.strip()) != len(tok_rep):
			if len(self.norm.strip()) + len_offset > len(tok_rep):
				self.unaligned_tokenization = tokenization
				tokenization = self.reconcile_tokenization(self.norm.strip(),tokenization)
				# Tokenization resulted in dropping characters
				#with io.open("errs.txt",'a',encoding="utf8") as f:
				#	f.write("WARN: unit '" + self.norm + "' tokenization shorter than input '" + tok_rep + "' (ignored)\n")
				#tokenization = self.norm
				self.tokenization = tokenization
			else:
				# Tokenization resulted in adding characters
				self.unaligned_tokenization = tokenization
				tokenization = self.reconcile_tokenization(self.norm.strip(),tokenization)
				#with io.open("errs.txt",'a',encoding="utf8") as f:
				#	f.write("WARN: unit '" + self.norm + "' tokenization longer than input '" + tok_rep + "' (ignored)\n")
				#tokenization = self.norm
				self.tokenization = tokenization
		cursor = len(self.norm) - 1
		for i in range(1, len(tokenization)):
			c = tokenization[-i]  # Traverse tokenized string backwards
			if c in self.tokenization_chars:
				position = self.norm_map[cursor+1] - 1 if cursor < len(self.norm) else self.norm_map[cursor]
				tokenized = tokenized[:position+1] + c + tokenized[position+1:]
			else:
				cursor -= 1
		self.tokenized = tokenized

	@staticmethod
	def reconcile_tokenization(unsegmented,segmented):
		output = ""
		offset = 0
		if unsegmented == "":
			return ""
		for i, c in enumerate(list(unsegmented)):
			if len(segmented) <= i+1+offset:
				if i+1 < len(unsegmented):  # Segmentation is over, append remaining characters to output
					output += unsegmented[i:]
				break
			else:
				if segmented[i+offset] in ["|","-"]:
					output += segmented[i+offset]
					offset += 1
				if segmented[i+offset] != unsegmented[i]:  # Character conflict
					while segmented[i+offset] != unsegmented[i]:
						if i+offset == len(segmented)-1:
							#if i + 1 < len(unsegmented): # Segmentation is over
							#	output += unsegmented[i+1:]
							break
						elif segmented[i+offset] in ["|","-"]:
							output += segmented[i+offset]
						offset += 1
					#if segmented[i+offset] == unsegmented[i]:
					#	output+=unsegmented[i]
				output += c
		output = re.sub(r'\|+','|',output)
		output = re.sub(r'-+','-',output)
		if output[-1] in ["|","-"]:
			output = output[:-1]
		if output[0] in ["|","-"]:
			output = output[1:]
		return output

	def serialize_sgml(self):
		out_sgml = '<norm_group norm_group="' + self.norm.replace("□","").replace("■","") + '">'
		if "||" in self.tokenized:
			self.tokenized = re.sub(r'\|\|(.)',r'|\1|',self.tokenized)  # Try to push boundary to next letter
		if "||" in self.tokenized and "||" not in self.tokenization:
			self.tokenized = self.tokenization  # Must use normalized tokenization to express
		escaped = self.protect_seps(self.tokenized)
		dirty_norms = escaped.split("|")
		clean_norms = self.tokenization.split("|")
		for i, norm in enumerate(dirty_norms):
			clean_norm = clean_norms[i].replace("-","").replace("□","").replace("■","")
			out_sgml += '<norm norm="'+clean_norm+'">'
			morphs = norm.split("-")
			clean_morphs = clean_norms[i].split("-")
			for j, morph in enumerate(morphs):
				if len(morphs) > 1:
					out_sgml += '<morph morph="'+clean_morphs[j].replace("□","").replace("■","")+'">'
				out_sgml += morph #.replace("□","").replace("■","")
				if len(morphs) > 1:
					out_sgml += '</morph>'
			out_sgml += '</norm>'
		out_sgml += '</norm_group>'
		out_sgml = self.restore_seps(out_sgml)
		out_sgml = out_sgml.replace(">",">\n")
		out_sgml = out_sgml.replace("<", "\n<")
		out_sgml = re.sub(r'\n+',r'\n',out_sgml)
		return out_sgml[1:]  # Trims leading newline

	@staticmethod
	def protect_seps(t):
		o = ""
		seps = ["|","-"]
		reps = ["@@@","$$$"]
		mode = "text"
		for c in t:
			if c == "<":
				mode = "xml"
			elif c ==">":
				mode = "text"
			if mode == "xml" and c in seps:
				o += reps[seps.index(c)]
			else:
				o += c
		return o

	@staticmethod
	def restore_seps(t):
		t = t.replace("@@@","|").replace("$$$","-")
		return t

	def __getattr__(self, item):
		if item == "tokenized" and self.out_tok_sep != "|":
			return self.tokenized.replace("|",self.out_tok_sep)
		else:
			if "__" not in item:
				return self.__dict__[item]
			elif item in self.__dict__:
				return self.__dict__[item]
			else:
				pass
				raise AttributeError("No attribute: " + str(item))
				#sys.stderr.write(item + " not in dict\n")

	def __repr__(self):
		return self.norm + " (" + self.dirty.replace("\\n","\n") + ")"


def add_lines(text):
	output = []
	lines = text.split("\n")
	for line in lines:
		if re.match(r"^<[^>]+>$",line):
			output.append(line)
		else:
			output.append("<line>" + line + "</line>")
	return "\n".join(output)


def dissolve(text, tok_sep="|", tokenized=False):

	mode = None
	bound_groups = [BoundGroup(out_tok_sep=tok_sep)]  # First bound group filled as position of pre-text XML

	for i, c in enumerate(text):
		if mode != "xml" and (c in [" ", "_"] and i != len(text)-1):  # bound group ends
			if not bound_groups[-1].norm == "": # Check previous group is non-empty
				bound_groups.append(BoundGroup(out_tok_sep=tok_sep))
		else:
			bound_groups[-1].affix(c,tokenized)

		if c == "<":
			mode = "xml"
		elif mode == "xml":
			if c == ">":
				mode = "text"

	if bound_groups[-1].norm.strip() == "":  # Trailing white space removal
		if bound_groups[-1].dirty.strip() != "":
			# Preserve non-token material in penultimate bound group
			for c in bound_groups[-1].dirty:
				bound_groups[-2].affix(c,tokenized)
		bound_groups.pop()

	return bound_groups


def serialize(groups,pipes=False,group_sep="_",tok_sep="|"):
	out_text = ""
	if not pipes:
		for g in groups:
			out_text += g.serialize_sgml()
	else:
		out_text = group_sep.join([g.tokenized for g in groups])
	out_text = out_text.replace("■","-").replace("□","|")  # Restore remaining escaped hyphens etc.
	return out_text


class StackedTokenizer:

	def __init__(self,lines=False,pipes=False,tokenized=False,no_morphs=False):
		self.lines = lines
		self.pipes = pipes
		self.tokenized = tokenized
		self.no_morphs = no_morphs
		self.load_rftokenizer()

	def load_rftokenizer(self):
		self.rf_tok = RFTokenizer(model="cop")

	def analyze(self,data):
		if self.lines:
			data = add_lines(data)

		if not PY3:
			data = unicode(data)
		grps = dissolve(data, tokenized=self.tokenized)

		if self.tokenized:
			for g in grps:
				# plain_tokenization = g.norm.replace("□","|").replace("■","-")
				plain_tokenization = g.pretokenization
				g.orig = g.orig.replace("□", "").replace("■", "")
				g.norm = g.norm.replace("□", "").replace("■", "")
				# g.dirty = g.dirty.replace("□","").replace("■","")
				g.add_tokenization(plain_tokenization)
		else:
			norms = [g.norm for g in grps]
			norm_types = list(set(norms))

			known_tokenizations = {}
			unknown = set([])

			tokenizations_lo = lookup_tokenize(norm_types, underscore_oov=True)
			# lo_not_found = [i for i,x in enumerate(tokenizations_lo) if x == '_']
			# tokenizations_lo = dict(zip(norm_types,tokenizations_lo))

			for norm, tokked in zip(norm_types, tokenizations_lo):
				if tokked == "_":
					unknown.add(norm)
				else:
					known_tokenizations[norm] = tokked

			to_tokenize = list(unknown)
			tokenizations_fs = fs_tokenize(to_tokenize)
			unknown = set([])

			for norm, tokked in zip(to_tokenize, tokenizations_fs):
				if "|" in tokked:
					if tokked.endswith("|"):
						tokked = tokked[:-1]
					known_tokenizations[norm] = tokked
				else:
					unknown.add(norm)

			unknown_indices = []
			for i, norm in enumerate(norms):
				if norm in unknown:
					unknown_indices.append(i)

			if not PY3:
				pass
			# norms = [norm.decode("utf8") for norm in norms]
			tokenizations_rf = self.rf_tok.rf_tokenize(norms, indices=unknown_indices)

			best_tokenizations = []
			j = 0
			for i, norm in enumerate(norms):
				if i in unknown_indices:
					best_tokenizations.append(tokenizations_rf[j])
					j += 1
				else:
					best_tokenizations.append(known_tokenizations[norm])

			# blender_features = get_blender_features()

			# for i in range(len(tokenizations_fs)):
			#	if tokenizations_lo[i] != "_":
			#		best_tokenizations.append(tokenizations_lo[i])
			#	elif "|" in tokenizations_fs[i]:
			#		best_tokenizations.append(tokenizations_fs[i])
			#	else:
			#		best_tokenizations.append(tokenizations_rf[i])

			m = MorphAnalyzer()
			for i, tokenization in enumerate(best_tokenizations):
				if not self.no_morphs:
					# print(tokenization)
					tokenization = m.analyze_morph(tokenization)
				grps[i].add_tokenization(tokenization)

		toks = serialize(grps, self.pipes)
		return toks

# toks = [g.tokenized for g in grps]


if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument("infile",action="store",help="Text, XML or SGML file with spaces or underscores between bound groups")
	parser.add_argument("-n","--no_morphs",action="store_true",dest="no_morphs",help="turn off morphological analysis (mnt- etc.)")
	parser.add_argument("-l","--lines",action="store_true",dest="lines", help="surround lines containing tokens with <line> tags")
	parser.add_argument("-p","--pipes",action="store_true",dest="pipes", help="output plain pipes and hyphens instead of SGML")
	parser.add_argument("-t","--tokenized",action="store_true",dest="tokenized", help="tokenization is already indicated via pipes and dashes")

	options = parser.parse_args()

	stk = StackedTokenizer(lines=options.lines,pipes=options.pipes,tokenized=options.tokenized,no_morphs=options.no_morphs)

	data = io.open(options.infile, encoding="utf8").read().replace("\r", "")

	toks = stk.analyze(data)

	if PY3:
		sys.stdout.buffer.write(toks.encode("utf8"))
	else:
		print(toks.encode("utf8"))

