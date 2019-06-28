#!/usr/bin/python
#  -*- coding: utf-8 -*-


from __future__ import unicode_literals
import sys, re, io, os
from six import iterkeys, itervalues
PY3 = sys.version_info[0] == 3

stk_dir = os.path.dirname(os.path.realpath(__file__))

cap_map = {"Ⲁ":"ⲁ","Ⲃ":"ⲃ","Ⲑ":"ⲑ","Ⲇ":"ⲇ","Ⲉ":"ⲉ","Ϥ":"ϥ","Ⲅ":"ⲅ","Ⲏ":"ⲏ","Ⲓ":"ⲓ","Ϫ":"ϫ","Ⲕ":"ⲕ","Ⲗ":"ⲗ","Ⲙ":"ⲙ","Ⲛ":"ⲛ","Ⲟ":"ⲟ","Ⲡ":"ⲡ","Ϭ":"ϭ","Ⲣ":"ⲣ","Ⲥ":"ⲥ","Ⲧ":"ⲧ","Ⲩ":"ⲩ","Ⲫ":"ⲫ","Ⲱ":"ⲱ","Ϩ":"ϩ","Ⲭ":"ⲭ","Ⲍ":"ⲍ","Ϣ":"ϣ","Ϯ":"ϯ","Ⲯ":"ⲯ","Ⲝ":"ⲝ"}

try:
	from .tokenize_fs import fs_tokenize
	from .tokenize_lookup import lookup_tokenize
	from .tokenize_rf import RFTokenizer
	from .tokenize_morph import MorphAnalyzer
except:
	from tokenize_fs import fs_tokenize
	from tokenize_lookup import lookup_tokenize
	from tokenize_rf import RFTokenizer
	from tokenize_morph import MorphAnalyzer

from argparse import ArgumentParser
from six import iteritems

if not PY3:
	reload(sys)
	sys.setdefaultencoding('utf8')
	from itertools import izip as zip

sys.path.append("lib")

class BoundGroup:

	# Static list of characters that are removed from norm text (basic normalization)
	orig_chars = ["̈", "", "̄", "̀", "̣", "`", "̅", "̈", "̂", "︤", "︥", "︦", "⳿", "~", "\n", "[", "]", "̇", "᷍"]
	tokenization_chars = ["|", "-"]

	def __init__(self, out_tok_sep="|"):
		self.dirty = ""
		self.norm = ""
		self.orig = ""
		self.tokenization = ""  # Holds the clean tokenization (a|f|sOtm)
		self.tokenized = ""  # Holds the dirty tokenization (a^|f|sO<hi rend="x">t</hi>m)
		self.unaligned_tokenization = ""  # Holds irregular, unalignable tokenization only expressible in SGML (n|t|he)
		self.pretokenization = ""  # Holds pre-specified tokenization (pipes in input)
		self.cursor = 0
		self.norm_cursor = 0
		self.mode = "text"
		self.norm_map = {}  # Dictionary from clean character position to dirty position, without seps
		self.merge_boundaries = []  # List of norm_map positions at which bound group merging has happened (during 'laytonization')
		self.out_tok_sep = out_tok_sep  # Separator to print between subtokens in 'pipes' mode
		self.proclitic = False  # Whether to join with next group ('laytonize')

	# Add a character to the bound group
	def affix(self, c, tokenized=False):

		if c == "|": # Input to ML tokenizer can't contain '|' or '-'
			if tokenized and self.mode!="xml":
				self.pretokenization = "".join([self.pretokenization,c])
				return None
			else:
				c = "□"
		elif c == "-":
			if tokenized and self.mode!="xml":
				self.pretokenization = "".join([self.pretokenization,c])
				return None
			else:
				c = "■"

		self.dirty = "".join([self.dirty,c])

		if c == "<":
			self.mode = "xml"

		if self.mode != "xml":
			if c in self.orig_chars:
				self.orig = "".join([self.orig,c])
				#self.norm_map[self.norm_cursor] = self.cursor
			else:
				self.orig = "".join([self.orig,c])
				if c == "⳯":  # ad-hoc normalization of superscript ni chracter
					c = "ⲛ"
				elif c in cap_map:
					c = cap_map[c]
				self.norm  = "".join([self.norm,c])
				if c not in ["□","■"] and tokenized:
					self.pretokenization  = "".join([self.pretokenization,c])
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
				tokenized = "".join([tokenized[:position+1], c, tokenized[position+1:]])
			else:
				cursor -= 1
		tokenized = tokenized.replace("[|","|[").replace("|]","]|")  # place pipes outside brackets
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
					output = "".join([output,unsegmented[i:]])
				break
			else:
				if segmented[i+offset] in ["|","-"]:
					output = "".join([output,segmented[i+offset]])
					offset += 1
				if segmented[i+offset] != unsegmented[i]:  # Character conflict
					while segmented[i+offset] != unsegmented[i]:
						if i+offset == len(segmented)-1:
							#if i + 1 < len(unsegmented): # Segmentation is over
							#	output += unsegmented[i+1:]
							break
						elif segmented[i+offset] in ["|","-"]:
							output = "".join([output, segmented[i + offset]])
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
			clean_norm = clean_norms[i].replace("-","")
			if len(clean_norm) > 1:
				clean_norm = clean_norm.replace("□","").replace("■","")
			out_sgml = "".join([out_sgml,'<norm norm="'+clean_norm+'">'])
			morphs = norm.split("-")
			clean_morphs = clean_norms[i].split("-")
			for j, morph in enumerate(morphs):
				if len(morphs) > 1:
					out_sgml = "".join([out_sgml,'<morph morph="'+clean_morphs[j].replace("□","").replace("■","")+'">'])
				out_sgml = "".join([out_sgml,morph]) #.replace("□","").replace("■","")
				if len(morphs) > 1:
					out_sgml = "".join([out_sgml,'</morph>'])
			out_sgml = "".join([out_sgml,'</norm>'])
		out_sgml = "".join([out_sgml,'</norm_group>'])
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
		textmode = True
		for c in t:
			if c == "<":
				textmode = False
			elif c ==">":
				textmode = True
			if not textmode and c in seps:
				o = "".join([o,reps[seps.index(c)]])
			else:
				o = "".join([o,c])
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
				raise AttributeError("No attribute: " + str(item))

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
		if c == "]":
			a=4
		if mode != "xml" and (c in [" ", "_"] and i != len(text)-1):  # bound group ends
			if bound_groups[-1].norm != "" or bound_groups[-1].dirty.strip() in ["[","]"]: # Check previous group is non-empty
				if bound_groups[-1].norm == "":  # Exception for user entered square bracket group
					bound_groups[-1].norm = bound_groups[-1].dirty.strip()
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


def find_non_sep_position(text, norm_position, norm_sep="|", morph_sep="-"):
	"""
	Finds the actual position of character n in a string, such that n is the
	number of characters traversed excluding separator chatacters

	:param text: the text to search for a position in
	:param norm_position: position ignoring separators
	:param norm_sep: norm separator to ignore when counting, default '|'
	:param norm_sep: morph separator to ignore when counting, default '-'
	:return: position in string not ignoring separators
	"""

	cursor = -1
	position = -1
	for c in text:
		position +=1
		if c != norm_sep and c != morph_sep:
			cursor +=1
			if cursor == norm_position:
				break
	return position


def serialize(groups,pipes=False,group_sep="_",tok_sep="|",segment_merged=False):
	out_text = ""
	if segment_merged:
		# Ensure that merged bound group positions have a separator, else add one
		for g in groups:
			if len(g.merge_boundaries) > 0:
				new_tokenization = g.tokenization
				for b in g.merge_boundaries:
					pos = find_non_sep_position(new_tokenization, b)
					#seps_before_boundary = new_tokenization[0:pos+1].count(tok_sep) + new_tokenization[0:pos+1].count("-")
					if new_tokenization[pos+1] != "-" and new_tokenization[pos+1] != tok_sep:
						new_tokenization = new_tokenization[0:pos+1] + "|" + new_tokenization[pos+1:]
				g.add_tokenization(new_tokenization)
	if not pipes:
		for g in groups:
			out_text += g.serialize_sgml()
	else:
		out_text = group_sep.join([g.tokenized for g in groups])
	out_text = out_text.replace("■","-").replace("□","|")  # Restore remaining escaped hyphens etc.
	return out_text


def adjust_theta(tokenization):
	"""Post-edit pre-tokenization in 'from pipes' mode to account for theta boundaries"""
	tokenization = tokenization.replace("ⲑ|","ⲧ|ϩ").replace("ⲑ-","ⲧ-ϩ")
	return tokenization


class StackedTokenizer:

	def __init__(self,lines=False,pipes=False,tokenized=False,no_morphs=False,detok=0,segment_merged=False,model="cop",ambig=None):
		self.lines = lines
		self.pipes = pipes
		self.tokenized = tokenized
		self.no_morphs = no_morphs
		self.model = model
		self.load_rftokenizer()
		self.ambig = {}
		if ambig is not None:
			self.load_ambig(ambig)
		self.load_rftokenizer()
		# Place-holders for detokenization mode (a.k.a. Laytonization)
		self.detokenize = detok
		self.segment_merged = segment_merged
		self.detok_table = None
		# Punctuation marks not to detokenize preceding bound groups into:
		self.no_merge = set(["·",".","·","ⲵ",",",":",";","ʼ","„","“"])
		if detok > 0:
			if detok > 1:
				self.load_detokenizer(aggressive=True)
			else:
				self.load_detokenizer(aggressive=False)

	def load_detokenizer(self,data=None,aggressive=False):
		if data is None:
			data = stk_dir + os.sep + ".." + os.sep + "data" + os.sep + "detok.tab"
		if os.path.exists(data):
			detoks = io.open(data,encoding="utf8").read().replace("\r","").strip().split("\n")
			split_lines = [(line.split("\t")[0], float(line.split("\t")[-1])) for line in detoks if not line.startswith("#")]
			if aggressive:
				split_lines = [(line[0].replace("%",""),line[1]) for line in split_lines]
			self.detok_table = set([line[0] for line in split_lines if line[1] >= 0.5])
		else:
			sys.stderr("x Stacked tokenizer could not load detok.tab at " + data)

	def load_ambig(self,ambig_table):
		lines = io.open(ambig_table,encoding="utf8").read().split("\n")
		for line in lines:
			if "\t" in line:
				fields = line.split("\t")
				self.ambig[fields[0]] = fields[1:]

	def load_rftokenizer(self):
		self.rf_tok = RFTokenizer(model=self.model)
		self.rf_tok.load()

	@staticmethod
	def merge_groups(last_grp, grp):
		"""
		Take two bound groups, the first of which is proctlitic, and merge them (i.e. 'laytonize')

		:param last_grp: proclitic group
		:param grp: following group to merge into
		:return:
		"""
		max_map = max(iterkeys(last_grp.norm_map))
		max_mapped = len(last_grp.dirty)-1 #max(itervalues(last_grp.norm_map))
		new_group = last_grp
		new_group.norm += grp.norm
		new_group.orig += grp.orig
		new_group.dirty += grp.dirty
		new_group.merge_boundaries.append(max_map)
		for key in grp.norm_map:
			new_group.norm_map[key + max_map + 1] = grp.norm_map[key] + max_mapped + 1
		new_group.proclitic = grp.proclitic

		return new_group

	def analyze(self,data):
		if self.lines:
			data = add_lines(data)

		if not PY3:
			data = unicode(data)
		grps = dissolve(data, tokenized=self.tokenized)

		if self.detokenize:
			for grp in grps:
				if grp.norm in self.detok_table:
					grp.proclitic = True
			last_grp = None
			detokenized = []
			for grp in grps:
				if last_grp is not None:
					if last_grp.proclitic or last_grp.norm in self.detok_table:
						if grp.norm not in self.no_merge:
							new_grp = self.merge_groups(last_grp,grp)
							last_grp = new_grp
							continue
					detokenized.append(last_grp)
				last_grp = grp
			if last_grp not in detokenized:
				detokenized.append(last_grp)
			grps = detokenized

		if self.tokenized:
			for g in grps:
				plain_tokenization = g.pretokenization
				plain_tokenization = adjust_theta(plain_tokenization)
				g.orig = g.orig.replace("□", "").replace("■", "")
				g.norm = g.norm.replace("□", "").replace("■", "")
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
				if len(norm) == 1:
					known_tokenizations[norm] = norm
				else:
					if tokked == "_" or norm in self.ambig:
						unknown.add(norm)
					else:
						known_tokenizations[norm] = tokked

			to_tokenize = list(unknown)
			tokenizations_fs = fs_tokenize(to_tokenize)
			unknown = set([])

			for norm, tokked in zip(to_tokenize, tokenizations_fs):
				if "|" in tokked and not norm in self.ambig:
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
					if norm in self.ambig:
						if tokenizations_rf[j] in self.ambig[norm]:
							best_tokenizations.append(tokenizations_rf[j])
							j+=1
							continue
						j+=1
						best_tokenizations.append(self.ambig[norm][0])
					else:
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

		toks = serialize(grps, self.pipes, segment_merged=self.segment_merged)

		return toks


if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument("infile",action="store",help="Text, XML or SGML file with spaces or underscores between bound groups")
	parser.add_argument("-n","--no_morphs",action="store_true",dest="no_morphs",help="turn off morphological analysis (mnt- etc.)")
	parser.add_argument("-l","--lines",action="store_true",dest="lines", help="surround lines containing tokens with <line> tags")
	parser.add_argument("-p","--pipes",action="store_true",dest="pipes", help="output plain pipes and hyphens instead of SGML")
	parser.add_argument("-t","--tokenized",action="store_true",dest="tokenized", help="tokenization is already indicated via pipes and dashes")
	parser.add_argument("-d","--detokenize",action="store_true",dest="detokenize", help="re-split boundgroups based on Layton's conventions")
	parser.add_argument("-s","--segment_merged",action="store_true",help="if detokenizing, force merged groups to hahve a boundary between them")

	options = parser.parse_args()

	stk = StackedTokenizer(lines=options.lines,pipes=options.pipes,tokenized=options.tokenized,no_morphs=options.no_morphs,
						   detok=options.detokenize, segment_merged=options.segment_merged)

	data = io.open(options.infile, encoding="utf8").read().replace("\r", "")

	toks = stk.analyze(data)

	if PY3:
		sys.stdout.buffer.write(toks.encode("utf8"))
	else:
		print(toks.encode("utf8"))
