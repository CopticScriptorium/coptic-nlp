#!/usr/bin/python
# -*- coding: utf-8 -*-

import io, os, re, sys
from collections import defaultdict
from six import iteritems

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
data_dir = script_dir + ".." + os.sep + "data" + os.sep

orig_chars = set(["̈", "", "̄", "̀", "̣", "`", "̅", "̈", "̂", "︤", "︥", "︦", "⳿", "~", "\n", "̇", " ", "‴", "#", "᷍", "⸍", "›", "‹"])


def clean(text):
	if "(" not in text and ")" not in text:  # Retain square brackets if item has capturing groups
		text = text.replace("[","").replace("]","")
	return ''.join([c for c in text if c not in orig_chars])


def no_paren(text):
	return re.sub(r'\(.*\)','',text).replace("^","")


class FSNorm:

	def __init__(self, grams=None, verbose=False):
		self.grams = set([]) if grams is None else set(grams)
		self.gram_len = len(list(self.grams)[0]) if len(self.grams) > 0 else 0
		lines = [clean(line).split("\t") for line in io.open(data_dir + "lexicon.tab",encoding="utf8").read().strip().split("\n") if "\t" in line and not "." in line]
		lexicon = defaultdict(list)

		if verbose:
			sys.stderr.write("o Full lexicon: " + str(len(lines)) +"\n")
		counter = 0
		for line in lines:
			if not self.gram_match(line[1]) and "(" not in line[1]:  # Skip lexicon entries with char n-grams not in input data
				continue
			lexicon[line[0]].append((line[1],line[2]))
			counter+=1

		if verbose:
			sys.stderr.write("o Filtered lexicon: " + str(counter) +"\n")

		lookup = defaultdict(lambda :defaultdict(str))
		lex = {}

		for i,cat in enumerate(lexicon):
			lex[cat] = "(?P<"+cat+"_>"+'|'.join(pair[0] for pair in lexicon[cat])+")"
			lookup[cat].update(dict((no_paren(pair[0]),pair[1]) for pair in lexicon[cat]))

		self.lookup = lookup

		patterns = []
		lines = io.open(data_dir + "grammar.tab",encoding="utf8").read().strip().split("\n")
		lines.sort(key=lambda x:len(x),reverse=True)
		for i, line in enumerate(lines):
			next_rule = False
			if len(line.strip()) > 0 and not line.startswith("#"):
				if "+" not in line:  # Unary rule
					line += "+"
				units = line.split("+")
				for unit in units:
					if unit not in lex and not unit == "":
						if verbose:
							sys.stdout.write("o Grammar contains rule " + line + " which has categories missing in the lexicon: " + unit+"\n")
						next_rule = True
				if next_rule:
					continue
				pattern = "(?P<"+line.replace("+","Q")+">"
				seen = []
				for unit in units:
					if unit == "":
						continue
					uptick = 0 if unit not in seen else seen.count(unit)
					unique_unit = lex[unit].replace("_>","_"+str(i+uptick)+">")
					pattern += unique_unit
					seen.append(unit)
				patterns.append(pattern+")")

		patterns = "|".join(patterns)
		self.bound_group = re.compile("^(" + patterns + ")$")

	def normalize(self,orig):

		orig = clean(orig)
		norm = ""
		for mo in self.bound_group.finditer(orig):
			match_groups = dict((key,val) for key, val in iteritems(mo.groupdict()) if mo.groupdict()[key] is not None)
			match_pats = [key for key in match_groups if "Q" in key]
			if len(match_pats) == 0:
				break
			else:
				pat = match_pats[0]
			parts = pat.split("Q")
			del match_groups[pat]
			for part in parts:
				for name, val in iteritems(match_groups):
					if "Q" in name:
						continue
					cat = re.sub("_[0-9]+$","",name)
					if cat == part:
						norm += self.lookup[cat][val]
						break
		if norm == "":
			norm = orig
		return norm

	def test(self,s,expected):
		try:
			val = self.normalize(s)
		except Exception as pe:
			print("Parsing failed:")
			print(s)
		else:
			print("'%s' -> %s" % (s, val), end=' ')
			if val == expected:
				print("CORRECT")
			else:
				print("***WRONG***, expected %s" % expected)

	def gram_match(self,text):
		"""Check if a word is necessary to compile into lexicon based on input char n-grams"""
		if len(text)<self.gram_len:
			return True
		elif len(self.grams) == 0:
			return True
		elif text[:self.gram_len] not in self.grams:
			return False
		elif text[-self.gram_len:] not in self.grams:
			return False
		return True


if __name__ == "__main__":

	fs = FSNorm()

	fs.test("ⲉⲧⲃⲉⲧϥⲭⲣⲓⲁ","ⲉⲧⲃⲉⲧⲉϥⲭⲣⲉⲓⲁ")

