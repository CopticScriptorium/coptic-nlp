#!/usr/bin/python
#  -*- coding: utf-8 -*-


from __future__ import unicode_literals
import sys, re, io, os
from six import iterkeys, iteritems
PY3 = sys.version_info[0] == 3

__version__ = "3.0.0"
__author__ = "Amir Zeldes"


stk_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = stk_dir + os.sep + ".." + os.sep + "data" + os.sep

sys.path.append(stk_dir)

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

if not PY3:
	reload(sys)
	sys.setdefaultencoding('utf8')
	from itertools import izip as zip

sys.path.append("lib")

from auto_norm import normalize as lookup_normalize

class BoundGroup:

	# Static list of characters that are removed from clean text (basic normalization)
	orig_chars = ["̈", "", "̄", "̀", "̣", "`", "̅", "̈", "̂", "︤", "︥", "︦", "⳿", "~", "\n", "[", "]", "̇", "᷍", "⸍", "›", "‹"]
	tokenization_chars = ["|", "-"]

	def __init__(self, out_tok_sep="|"):
		self.dirty = ""  # Holds input string of bound group with diacritics, XML and whitespace
		self.clean = ""  # Holds cleaned input string, without diacritics or XML/whitespace
		self.norm = ""   # Holds normalized version of bound group without XML/whitespace
		self.orig = ""   # Holds unnormalized, diplomatic version of bound group, with diacritics but no XML/whitespace
		self.tokenization = ""  # Holds the normalized tokenization (a|f|sOtm)
		self.tokenized = ""  # Holds the dirty tokenization (a^|f|sO<hi rend="x">t</hi>m)
		self.unaligned_tokenization = ""  # Holds irregular, unalignable tokenization only expressible in SGML (n|t|he)
		self.pretokenization = ""  # Holds pre-specified tokenization (pipes in input)
		self.cursor = 0
		self.clean_cursor = 0
		self.mode = "text"
		self.clean_map = {}  # Dictionary from clean character position to dirty position, without seps
		self.merge_boundaries = []  # List of clean_map positions at which bound group merging has happened (during 'laytonization')
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
				#self.clean_map[self.clean_cursor] = self.cursor
			else:
				self.orig = "".join([self.orig,c])
				if c == "⳯":  # ad-hoc normalization of superscript ni chracter
					c = "ⲛ"
				elif c in cap_map:
					c = cap_map[c]
				self.clean  = "".join([self.clean, c])
				if c not in ["□","■"] and tokenized:
					self.pretokenization  = "".join([self.pretokenization,c])
				self.clean_map[self.clean_cursor] = self.cursor
				self.clean_cursor += 1

		if c == ">":
			self.mode = "text"

		self.cursor += 1

	def add_tokenization(self, tokenization):
		# Move tokenization to norm form if tokenizing from pipes
		if self.pretokenization != "":
			if len(self.clean.strip()) != len(self.norm):
				tokenization = self.reconcile_tokenization(self.norm, tokenization)

		# Retain real tokenization for SGML output
		self.tokenization = tokenization

		# Construct approximate tokenization for piped output
		if ("ⲑ" in self.dirty or "Ⲑ" in self.dirty) and ("ⲧ|ϩ" in tokenization or "ⲧ-ϩ" in tokenization) and "ⲧϩ" not in self.dirty:
			tokenization = tokenization.replace("ⲧ|ϩ","ⲑ|").replace("ⲧ-ϩ","ⲑ-")
		if ("ⲫ" in self.dirty or "Ⲫ" in self.dirty) and ("ⲡ|ϩ" in tokenization or "ⲡ-ϩ" in tokenization) and "ⲡϩ" not in self.dirty:
			tokenization = tokenization.replace("ⲡ|ϩ","ⲫ|").replace("ⲡ-ϩ","ⲫ-")
		if "ϯ" in self.dirty and "ⲧ|ⲓ" in tokenization and "ⲧⲓ" not in self.dirty:
			tokenization = tokenization.replace("ⲧ|ⲓ","|ϯ")  # For cases like orig mpa|ti|-..., norm mapt|i|-
			if "||ϯ" in tokenization:
				tokenization = tokenization.replace("||ϯ","|ϯ|")  # For cases like orig ti|rHnH, norm t|irHnH
		if "ⲉⲧⲛⲁ" in self.dirty and "ⲉⲧⲛ|ⲛⲁ" in tokenization and "ⲉⲧⲛⲛⲁ" not in self.dirty:
			tokenization = tokenization.replace("ⲉⲧⲛ|ⲛⲁ","ⲉⲧⲛ|ⲁ")
		tokenized = self.dirty
		tok_rep = tokenization.replace("|","").replace("-","").strip()
		if len(self.clean.strip()) != len(tok_rep):  # Tokenization resulted in different number of characters than orig
			tokenization = self.reconcile_tokenization(self.clean.strip(), tokenization)
			if tokenization != "":
				self.unaligned_tokenization = tokenization
			else:  # Could not align normalized tokenization, revert everything to unsegmented clean form
				sys.stderr.buffer.write(("WARN: Could not reconcile normalized tokenization: " + self.clean.strip() + "<>" + self.tokenization + "\n").encode("utf8"))
				self.tokenization = self.unaligned_tokenization = self.norm = self.clean
		cursor = len(self.clean) - 1
		if self.unaligned_tokenization != "":
			tokenization = self.unaligned_tokenization
		for i in range(1, len(tokenization)):
			c = tokenization[-i]  # Traverse tokenized string backwards
			if c in self.tokenization_chars:
				position = self.clean_map[cursor + 1] - 1 if cursor < len(self.clean) else self.clean_map[cursor]
				tokenized = "".join([tokenized[:position+1], c, tokenized[position+1:]])
			else:
				cursor -= 1
		tokenized = tokenized.replace("[|","|[").replace("|]","]|")  # place pipes outside brackets
		self.tokenized = tokenized

	@staticmethod
	def reconcile_tokenization(unsegmented, segmented):
		"""Function to insert separators from `segmented` into a similar string `unsegmented`.

		Behavior:
		1. Characters are traversed in both strings in tandem, with boundaries inserted into unsegmented wherever matching positions are found
		2. If there is a non-separator character mismatch, the algorithm waits until a match is found, inserting characters from the longer string
		3. Traversal is automatically tied to the longer string
		4. LTR traversal is preferred, RTL is attempted if LTR alignment is impossible
		5. Returns empty string if no alignment is possible

		Examples:
		  reconcile_tokenization("ⲡⲉⲭⲥ","ⲡⲉ|ⲭⲣⲓⲥⲧⲟⲥ") -> ⲡⲉ|ⲭⲥ (scans LTR, inserts seg after pe|, matches x, waits until s is matched)
		  reconcile_tokenization("ⲡⲉⲭ","ⲡⲉ|ⲭⲣⲓⲥⲧⲟⲥ") -> ⲡⲉ|ⲭ (scans LTR, match pe|, x ... quits because unsegmented string is done)
		  reconcile_tokenization("ⲙⲛⲡⲉⲕⲉⲓⲱⲧ","ⲙⲛ|ⲡⲕ|ⲉⲓⲱⲧ") -> ⲙⲛ|ⲡⲉⲕ|ⲉⲓⲱⲧ  (scans mn|p.. waits for k, inserts e, finds k, continues alignment)
		  reconcile_tokenization("ⲉⲧⲣⲉϥϩⲉ","ⲉ|ⲧⲣ|ϥ|ϩⲉ") -> ⲉ|ⲧⲣⲉ|ϥ|ϩⲉ (exception for |ⲧⲣ|, does not output expected ⲉ|ⲧⲣ|ⲉϥ|ϩⲉ)
		  reconcile_tokenization("ⲛⲡⲭⲣⲓⲥⲧⲟⲥ","ⲙ|ⲡⲉ|ⲭⲣⲓⲥⲧⲟⲥ") -> (scans LTR, fails since ⲛ never appears, scans RTL and succeeds, appending left over ⲛ to start)
		  reconcile_tokenization("ⲡⲉⲭ","ⲫⲗ|ⲥ") -> "" (both directions fail)

		"""

		def consecutive_seps(text):
			if "||" in text or "--" in text or "|-" in text or "-|" in text:
				return True
			if text.startswith("|") or text.endswith("|") or text.startswith("-") or text.endswith("-"):
				return True
			return False

		def align(unsegmented, segmented, reverse=False, loose=False):
			seps = set(["|","-"])
			clean_seg = segmented.replace("|","").replace("-","")
			output = ""
			offset = 0
			revoffset = 0
			if reverse:
				unsegmented = unsegmented[::-1]
				segmented = segmented[::-1]
			# Traverse by longer string
			if len(clean_seg) > len(unsegmented):
				for i, c in enumerate(unsegmented):
					if i+offset > len(segmented)-1:  # Segmented string ended without perfect alignment, try to append rest
						output += c
						continue
					if segmented[i+offset] in seps:
						output += segmented[i+offset]
						offset += 1  # Move cursor in unsegmented to account for separator
					while c != segmented[i+offset]: # Mismatch: keep chomping longer string until match
						if loose and c == "ϯ" and segmented[i+offset] == "ⲧ":
							break
						if segmented[i+offset] in seps:
							output += segmented[i+offset]
						offset += 1
						if i+offset > len(segmented)-1:  # Segmented string ended without match, end chomping
							break
					output += c
			else:
				done = False
				for i, c in enumerate(unsegmented):
					if i+offset < len(segmented):
						if segmented[i+offset] in seps:
							output += segmented[i+offset]
							offset += 1
						if i+revoffset == len(unsegmented):
							# Unsegmented has been spelled out, alignment
							break
						while unsegmented[i+revoffset] != segmented[i+offset]:
							if loose and unsegmented[i+revoffset] == "ϯ" and segmented[i+offset] == "ⲧ":
								break
							if loose and revoffset > 0:
								if unsegmented[i+revoffset-1:i+revoffset+1] == "ⲧⲓ" and segmented[i+offset] == "ϯ":
									# segmentation has ϯ and unsegmented has ⲧⲓ
									break
							output += unsegmented[i+revoffset]
							revoffset += 1
							if i+revoffset > len(unsegmented)-1:  # Segmented string ended without match, end chomping
								done = True
								break
						if done:
							break
						else:
							output += unsegmented[i+revoffset]
					else:  # Check for left over characters
						if len(unsegmented) > i+revoffset:
							output += unsegmented[i+revoffset:]
							break
			if reverse:
				output = output[::-1]
			return output

		# Case 1: try LTR alignment
		output = align(unsegmented,segmented)
		# Case 2: try RTL alignment
		if consecutive_seps(output):
			# Mapping failed, traverse longer string RIGHT TO LEFT
			output = align(unsegmented,segmented,reverse=True)
		if (consecutive_seps(output) and "ϯ" in unsegmented) or ("ϯ|" in segmented and "|" not in output):
			# Mapping failed, traverse longer string RIGHT TO LEFT
			output = align(unsegmented,segmented,loose=True)
			if consecutive_seps(output):
				output = align(unsegmented,segmented,loose=True,reverse=True)
		if "||ⲑ" in output and "ⲧ|ⲑ" in segmented:
			output = output.replace("||ⲑ","|ⲑ|")

		output = re.sub(r'\|+','|',output)
		output = re.sub(r'-+','-',output)
		if "|ⲧⲣ|ⲉ" in output:  # tr|f -> tre|f is an exception to left-to-right alignment priority
			output = output.replace("|ⲧⲣ|ⲉ","|ⲧⲣⲉ|")
		if output[-1] in ["|","-"]:
			output = output[:-1]
		if output[0] in ["|","-"]:
			output = output[1:]
		if output.count("|") != segmented.count("|"):
			output=""

		return output

	def serialize_sgml(self):
		out_sgml = '<norm_group norm_group="' + self.norm.replace("□", "").replace("■", "") + '">'
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
		if len(self.norm)==0:
			return "C: " + self.clean + " (" + self.dirty.replace("\\n", "\n") + ")"
		else:
			return "N: " + self.norm + " (" + self.dirty.replace("\\n", "\n") + ")"


def add_lines(text, counter=True):
	output = []
	lines = text.split("\n")
	lnum = 1
	for line in lines:
		if counter:
			if "<pb " in line or "<pb>" in line or "<pb_xml" in line:
				lnum = 1
		if re.match(r"^<[^>]+>$",line):
			output.append(line)
		else:
			if counter:
				output.append('<lb n="'+str(lnum)+'">' + line + "</lb>")
				lnum += 1
			else:
				output.append("<line>" + line + "</line>")
	return "\n".join(output)


def dissolve(text, tok_sep="|", tokenized=False):

	mode = None
	bound_groups = [BoundGroup(out_tok_sep=tok_sep)]  # First bound group filled as position of pre-text XML

	for i, c in enumerate(text):
		if mode != "xml" and (c in [" ", "_"] and i != len(text)-1):  # bound group ends
			if bound_groups[-1].clean != "" or bound_groups[-1].dirty.strip() in ["[", "]"]: # Check previous group is non-empty
				if bound_groups[-1].clean == "":  # Exception for user entered square bracket group
					bound_groups[-1].clean = bound_groups[-1].dirty.strip()
				bound_groups.append(BoundGroup(out_tok_sep=tok_sep))
		else:
			bound_groups[-1].affix(c,tokenized)

		if c == "<":
			mode = "xml"
		elif mode == "xml":
			if c == ">":
				mode = "text"

	if bound_groups[-1].clean.strip() == "":  # Trailing white space removal
		if bound_groups[-1].dirty.strip() != "":
			# Preserve non-token material in penultimate bound group
			for c in bound_groups[-1].dirty:
				bound_groups[-2].affix(c,tokenized)
		bound_groups.pop()

	return bound_groups


def find_non_sep_position(text, norm_position, norm_sep="|", morph_sep="-"):
	"""
	Finds the actual position of character n in a string, such that n is the
	number of characters traversed excluding separator characters

	:param text: the text to search for a position in
	:param norm_position: position ignoring separators
	:param norm_sep: clean separator to ignore when counting, default '|'
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
		for i,g in enumerate(groups):
			if len(g.merge_boundaries) > 0:
				new_tokenization = g.tokenization
				for b in g.merge_boundaries:
					pos = find_non_sep_position(new_tokenization, b)
					#seps_before_boundary = new_tokenization[0:pos+1].count(tok_sep) + new_tokenization[0:pos+1].count("-")
					if len(new_tokenization) > pos+1:
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

	def __init__(self,lines=False,pipes=False,tokenized=False,no_morphs=False,detok=0,segment_merged=False,model="cop",
				 ambig=None,use_meta=False,model_path=None,morph_table=None):
		self.lines = lines
		self.pipes = pipes
		self.tokenized = tokenized
		self.no_morphs = no_morphs
		self.model = model
		self.load_rftokenizer(model_path=model_path)
		self.ambig = {}
		if ambig is not None:
			self.load_ambig(ambig)
		self.use_meta = use_meta
		if self.use_meta:
			try:
				from .tokenize_meta import MetaTokenizer
			except:
				from tokenize_meta import MetaTokenizer
			self.metatok = MetaTokenizer(model="cop",rf_tok=self.rf_tok)
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
		self.escaped_squares = False
		self.morph_analyzer = MorphAnalyzer(morph_table=morph_table)

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

	def load_rftokenizer(self, model_path=None):
		self.rf_tok = RFTokenizer(model=self.model)
		if model_path is None:
			self.rf_tok.load()
		else:
			self.rf_tok.load(model_path=model_path)

	def normalize(self,groups,norm_table=None):
		cleans = [g.clean for g in groups]
		if norm_table is None:
			norms = lookup_normalize("\n".join(cleans),table_file=data_dir+"norm_table.tab").split("\n")
		else:
			norms = lookup_normalize("\n".join(cleans),table_file=norm_table).split("\n")

		for i,g in enumerate(groups):
			g.norm = norms[i]

		return groups

	@staticmethod
	def merge_groups(last_grp, grp):
		"""
		Take two bound groups, the first of which is proctlitic, and merge them (i.e. 'laytonize')

		:param last_grp: proclitic group
		:param grp: following group to merge into
		:return:
		"""
		max_map = max(iterkeys(last_grp.clean_map))
		max_mapped = len(last_grp.dirty)-1 #max(itervalues(last_grp.clean_map))
		new_group = last_grp
		new_group.clean += grp.clean
		new_group.norm += grp.norm
		new_group.orig += grp.orig
		new_group.dirty += grp.dirty
		new_group.merge_boundaries.append(max_map)
		for key in grp.clean_map:
			new_group.clean_map[key + max_map + 1] = grp.clean_map[key] + max_mapped + 1
		new_group.proclitic = grp.proclitic

		return new_group

	def analyze(self,data,do_normalize=True,norm_table=None):
		if '□' in data:
			data = data.replace('□','▫')
			self.escaped_squares = True
		else:
			self.escaped_squares = False

		if self.lines:
			data = add_lines(data)

		if not PY3:
			data = unicode(data)
		grps = dissolve(data, tokenized=self.tokenized)

		if self.detokenize in [1,2]:
			for grp in grps:
				if grp.clean in self.detok_table:
					grp.proclitic = True
		elif self.detokenize == 3:
			import binder # import here to avoid circular dep
			binding_predictions = binder.predict(" ".join([grp.orig for grp in grps]))
			for i, pred in enumerate(binding_predictions):
				if pred >= 0.5:
					grps[i].proclitic = True

		if self.detokenize > 0:
			last_grp = None
			detokenized = []
			for grp in grps:
				if last_grp is not None:
					if last_grp.proclitic or (last_grp.clean in self.detok_table and self.detokenize in [1,2]):
						if grp.clean not in self.no_merge:
							new_grp = self.merge_groups(last_grp,grp)
							last_grp = new_grp
							continue
					detokenized.append(last_grp)
				last_grp = grp
			if last_grp not in detokenized:
				detokenized.append(last_grp)
			grps = detokenized

		if self.tokenized:
			if do_normalize:
				grps = self.normalize(grps,norm_table=norm_table)
				#for g in grps:
				#	g.clean = g.norm
			for g in grps:
				plain_tokenization = g.pretokenization
				plain_tokenization = adjust_theta(plain_tokenization)
				g.orig = g.orig.replace("□", "").replace("■", "")
				g.clean = g.clean.replace("□", "").replace("■", "")
				g.add_tokenization(plain_tokenization)
		else:
			if do_normalize:
				grps = self.normalize(grps,norm_table=norm_table)
			else:
				for g in grps:
					g.norm = g.clean

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
				if norm in unknown:# or clean in self.ambig:
					unknown_indices.append(i)

			if not PY3:
				pass
			# norms = [clean.decode("utf8") for clean in norms]
			tokenizations_rf = self.rf_tok.rf_tokenize(norms, indices=unknown_indices)

			if self.use_meta:
				tokenizations_meta, believe_fs, meta_probas = self.metatok.predict(norms)

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
					if known_tokenizations[norm] in tokenizations_lo or not self.use_meta:
						best_tokenizations.append(known_tokenizations[norm])
					elif meta_probas[i] > 0.1:
						best_tokenizations.append(known_tokenizations[norm])
					else:
						best_tokenizations.append(tokenizations_meta[i])

			# blender_features = get_blender_features()

			# for i in range(len(tokenizations_fs)):
			#	if tokenizations_lo[i] != "_":
			#		best_tokenizations.append(tokenizations_lo[i])
			#	elif "|" in tokenizations_fs[i]:
			#		best_tokenizations.append(tokenizations_fs[i])
			#	else:
			#		best_tokenizations.append(tokenizations_rf[i])

			m = self.morph_analyzer
			prev_tokenization = ""
			overrides = {"ⲉ|ⲡ|ⲁϩⲟ": "ⲉ|ⲡⲁ|ϩⲟ", "ⲛⲉ|ⲛ|ⲕⲁ": "ⲛⲉ|ⲛⲕⲁ", "ⲉ|ⲧⲟⲩ|ϯⲥⲃⲱ": "ⲉⲧ|ⲟⲩ|ϯⲥⲃⲱ","ⲛ|ⲉⲛⲧ|ⲁ|ⲩ|ϫⲟⲟⲩ":"ⲛ|ⲉⲛⲧ|ⲁ|ⲩ|ϫⲟ|ⲟⲩ"}
			substrings = {"ⲛⲉ|ⲩ|ⲛ|ⲟⲩ|": "ⲛⲉ|ⲩⲛ|ⲟⲩ|","ⲛⲉ|ⲩ|ⲛ|ϩⲉⲛ|":"ⲛⲉ|ⲩ|ⲛ|ϩⲉⲛ|","ϫⲟ|ⲟⲩ|ⲥⲉ":"ϫⲟⲟⲩ|ⲥⲉ"}
			for i, tokenization in enumerate(best_tokenizations):
				if not self.no_morphs:
					# print(tokenization)
					tokenization = m.analyze_morph(tokenization)
				# Hard wired rare but reliable solutions based on adjacent bound group
				if i > 0:
					prev_tokenization = best_tokenizations[i - 1]
					if tokenization == "ⲙⲙⲟ|ⲛ":
						if prev_tokenization.split("|")[-1] in ["ϫⲓⲛ","ϫⲉ","ϫⲛ","ⲉϣⲱⲡⲉ"]:
							tokenization = "ⲙⲙⲟⲛ"
				if i < len(best_tokenizations) - 1:
					next_tokenization = best_tokenizations[i+1]
					if tokenization == "ⲛ|ⲧⲉⲧⲛ" and next_tokenization.split("|")[0] in ["ⲛ","ϩⲉⲛ"]:
						tokenization = "ⲛⲧⲉⲧⲛ"
				if tokenization in overrides:
					tokenization = overrides[tokenization]
				for f, r in iteritems(substrings):
					tokenization = tokenization.replace(f,r)

				grps[i].add_tokenization(tokenization)

		toks = serialize(grps, pipes=self.pipes, segment_merged=self.segment_merged)

		if self.escaped_squares:
			toks = toks.replace('▫','□')

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
	parser.add_argument("-v","--version",action="store_true",help="print version number and quit")

	if "-v" in sys.argv or "--version" in sys.argv:
		print("Stacked Tokenizer V" + __version__)
		sys.exit(1)

	options = parser.parse_args()

	stk = StackedTokenizer(lines=options.lines,pipes=options.pipes,tokenized=options.tokenized,no_morphs=options.no_morphs,
						   detok=options.detokenize, segment_merged=options.segment_merged,ambig=data_dir+"ambig.tab")

	data = io.open(options.infile, encoding="utf8").read().replace("\r", "")

	toks = stk.analyze(data)

	if PY3:
		sys.stdout.buffer.write(toks.encode("utf8"))
	else:
		print(toks.encode("utf8"))
