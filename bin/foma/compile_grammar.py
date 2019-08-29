#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Script to generate categorized normalization inventory which feeds into
a Xerox FSM format normalization scripts to generate a .lexc file
"""

import io, os, sys, re
from collections import defaultdict
import subprocess

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
data_dir = script_dir + ".." + os.sep + ".." + os.sep + "data" + os.sep
eval_dir = script_dir + ".." + os.sep+ ".." + os.sep + "eval" + os.sep

orig_chars = set(["̈", "", "̄", "̀", "̣", "`", "̅", "̈", "̂", "︤", "︥", "︦", "⳿", "~", "\n", "̇", " ", "‴", "#", "᷍", "⸍", "›", "‹"])
vowels = list("ⲁⲉⲓⲟⲩⲏⲱ")


def clust(word):
	"""Check if word begins with consonant cluster"""
	if len(word) < 2:
		return False
	else:
		if word[0] not in vowels and word[1] not in vowels:
			return True
		elif word[0] in ["ⲯ","ⲭ","ⲑ","ⲫ","ⲝ"]:
			return True
		elif word in ["ϩⲟⲟⲩ","ⲟⲩⲟⲉⲓϣ","ⲩⲟⲉⲓϣ","ⲣⲟⲙⲡⲉ","ⲟⲩϣⲏ","ⲩϣⲏ","ⲟⲩⲛⲟⲩ","ⲩⲛⲟⲩ"]:
			return True
	return False


def initial(word,letter):
	if len(word) < 2:
		return False
	else:
		if word[0]==letter:
			return True
	return False


def starter(word,starts):
	for starter in starts:
		if word.startswith(starter):
			return True
	return False


def clean(text):
	if not text in ["[","]"]:
		for c in orig_chars:
			text = text.replace(c,"")
	return text.lower()


def mutate(find,rep,source_dict,target_dict,exclude=None):
	"""Use a regex find/replace pattern to create variants of keys in source dict, and introduce them into
	target dict with source dict form as the normalization (unless they are in the iterable `exclude')"""

	for word in source_dict:
		if word == "ϫⲓ":
			a=4
		matches = list(re.finditer(find,word))
		if len(matches)>0:  # Replace all instances
			mutated = re.sub(find,rep,word)
			if mutated not in exclude and mutated not in source_dict:  # Make sure the variant is not attested as something else
				target_dict[mutated] = source_dict[word]
			if len(matches)>1:  # Get individual replacements as well, since there are multiple instances
				for m in matches:
					prefix = re.escape(word[:m.start()])
					suffix = re.escape(word[m.end():])
					mutated = re.sub(prefix+find+suffix,prefix+rep+suffix,word).replace("\\","")
					if mutated not in exclude and mutated not in source_dict:  # Make sure the variant is not attested as something else
						target_dict[mutated] = source_dict[word]

	return target_dict

def make_lexicon_foma():
	"""Make the human-readable three column file lexicon_foma.tab in the format:
	category	orig	norm
	...

	This file is later transformed into a XFST format .lexc cascade using grammar_foma.tab

	"""

	# Known problematic/non-standard spellings in copt_lemma_lex
	forbidden = set(["ⲛⲏⲥⲧⲓⲁ","ⲁⲡⲓⲗⲏ","ⲁⲣⲭⲓ","ⲙⲟⲛⲟⲭⲟⲥ","ⲙⲛⲧⲙⲟⲛⲟⲭⲟⲥ","ⲙⲉⲓⲗⲓⲟⲛ","ⲓⲱⲧ","ⲣϫⲟⲓⲥ","ϫⲟⲓⲥ","ⲁⲓⲧⲓ","ⲭⲣⲓⲁ","ⲣⲭⲣⲓⲁ","ⲣⲉϥⲣⲭⲣⲓⲁ","ⲫⲟⲣⲓ",
					 "ⲕⲟⲩⲉⲓ","ⲉⲛⲉⲣⲅⲓ","ⲙⲉⲧⲁⲛⲟⲓ","ϩⲟⲉⲓⲧⲉ","ⲧⲉⲓ","ⲧⲉⲉⲓ","ⲙⲙⲉ","ⲟⲩⲟⲉⲓ"])
	never_normalize = set(["ϫ"])

	norm_data = io.open(data_dir + "norm_table.tab",encoding="utf8").read().strip().replace("\r","").split("\n")
	norms = dict((line.split("\t")) for line in norm_data if "\t" in line)
	all_norms = set([])
	for orig, norm in norms.items():
		all_norms.add(clean(norm))
	for orig, norm in norms.items():
		orig = clean(orig).lower()
		if orig != clean(norm) and orig not in all_norms:
			if re.search(r'[ⲁⲃⲅⲇⲉⲍⲏⲑⲕⲗⲙⲛⲥⲟⲡⲣⲧⲭⲯⲝⲱⲩϫϥϩϭϣϯ]',orig) is not None:
				forbidden.add(orig)


	# Determiners
	all_pos_m = ["ⲡⲁ","ⲡⲉⲕ","ⲡⲟⲩ","ⲡⲉϥ","ⲡⲉⲥ","ⲡⲉⲛ","ⲡⲉⲧⲛ","ⲡⲉⲩ"]
	all_pos_f = [p.replace("ⲡ","ⲧ") for p in all_pos_m]
	all_pos_pl = [p.replace("ⲡ","ⲛ") for p in all_pos_m]
	all_pos_m = {k:k for k in all_pos_m}
	all_pos_f = {k:k for k in all_pos_f}
	all_pos_pl = {k:k for k in all_pos_pl}

	art_m = {"ⲡ":"ⲡ","ⲡⲕⲉ":"ⲡⲕⲉ","ⲟⲩ":"ⲟⲩ","ⲟⲩⲕⲉ":"ⲟⲩⲕⲉ","ⲡⲉⲓ":"ⲡⲉⲓ","ⲡⲉⲉⲓ":"ⲡⲉⲓ"}
	art_f = {"ⲧ":"ⲧ","ⲧⲕⲉ":"ⲧⲕⲉ","ⲟⲩ":"ⲟⲩ","ⲟⲩⲕⲉ":"ⲟⲩⲕⲉ","ⲧⲉⲓ":"ⲧⲉⲓ","ⲧⲉⲉⲓ":"ⲧⲉⲓ"}
	art_pl = {"ⲛ":"ⲛ","ⲛⲕⲉ":"ⲛⲕⲉ","ϩⲉⲛ":"ϩⲉⲛ","ϩⲉⲛⲕⲉ":"ϩⲉⲛⲕⲉ","ⲛⲉⲓ":"ⲛⲉⲓ","ⲛⲉⲉⲓ":"ⲛⲉⲓ"}

	art_m.update(all_pos_m)
	art_f.update(all_pos_f)
	art_pl.update(all_pos_pl)
	art_pl_r = {"ⲣ":"ⲛ"}
	art_pl_l = {"ⲗ":"ⲛ"}
	art_pl_b = {"ⲃ":"ⲛ"}

	art_m_long = {"ⲡⲉ":"ⲡⲉ"}
	art_f_long = {"ⲧⲉ":"ⲧⲉ"}
	art_pl_long = {"ⲛⲉ":"ⲛⲉ"}

	art_theta = {"ⲑ":"ⲧ"}
	art_eth = {"ⲉⲑ":"ⲉⲧ","ⲡⲉⲑ":"ⲡⲉⲧ","ⲛⲉⲑ":"ⲛⲉⲧ","ⲧⲉⲑ":"ⲧⲉⲧ"}
	art_phi = {"ⲫ":"ⲡ"}

	# Converters and initial je
	conv = {"ⲉⲣⲉ":"ⲉⲣⲉ","ⲛⲉⲣⲉ":"ⲛⲉⲣⲉ","ⲉⲧⲉⲣⲉ":"ⲉⲧⲉⲣⲉ"}
	conv_short = {"ⲉ":"ⲉ","ⲛⲉ":"ⲛⲉ"}
	et = {"ⲉⲧ":"ⲉⲧ"}
	je = {"ϫⲉ":"ϫⲉ"}
	na = {"ⲛⲁ":"ⲛⲁ"}
	ta = {"ⲧⲁ":"ⲧⲁ"}

	# Prepositions
	prep = ["ⲉ","ⲉⲧⲃⲉ","ϣⲁ","ⲛⲥⲁ","ⲕⲁⲧⲁ","ⲙⲛ","ⲁϫⲛ","ⲛⲧⲉ","ⲛⲃⲗ","ⲉⲣⲁⲧ","ϩⲁ","ⲡⲁⲣⲁ","ⲛⲁ","ⲛⲧⲉ","ⲛϭⲓ","ⲭⲱⲣⲓⲥ","ϣⲉ"]  # not nqi, Se not really a prep
	prep_m = ["ⲙ","ϩⲁⲧⲙ","ϩⲓⲣⲙ","ϩⲙ","ϩⲓⲧⲙ","ϩⲓϫⲙ","ⲉϫⲙ"]
	prep_n = ["ⲛ","ϩⲁⲧⲛ","ϩⲓⲣⲛ","ϩⲛ","ϩⲓⲧⲛ","ϩⲓϫⲛ","ⲉϫⲛ"]
	prep = prep + prep_n

	prep_no_tn ={"ϩⲓ":"ϩⲓ"}

	ppos_f = {"ⲧⲕ̄":"ⲧⲉⲕ","ⲧϥ̄":"ⲧⲉϥ","ⲧⲛ":"ⲧⲉⲛ"}  # watch out for hitn- becoming hi-ten-, e-ten, n-ten
	ppos_m = {"ⲡⲕ̄":"ⲡⲉⲕ","ⲡϥ̄":"ⲡⲉϥ","ⲡⲛ̄":"ⲡⲉⲛ"}
	ppos_pl = {"ⲛⲕ̄":"ⲛⲉⲕ"}  # skip "ⲛⲛ̄":"ⲛⲉⲛ" since it can be normal n|n|-
	nf = {"ⲛϥ̄":"ⲛⲉϥ"}  # Spectial entry for nf- to prevent overgeneration for actual conjunctive n|f|sOtm

	art_m.update(ppos_m)
	art_f.update(ppos_f)
	art_pl.update(ppos_pl)

	# Nouns
	noun_f = set(["ϩⲓⲙⲉ","ⲙⲏⲧⲉ","ⲙⲓⲛⲉ","ϭⲟⲙ","ⲥⲁⲣⲝ","ϩⲉ","ⲉⲡⲓⲥⲧⲟⲗⲏ","ⲉⲕⲕⲗⲏⲥⲓⲁ","ⲙⲛⲧⲣⲣⲟ","ϩⲏ","ⲡⲟⲣⲛⲉⲓⲁ","ⲡⲟⲣⲛⲏ","ⲯⲩⲭⲏ","ⲙⲁⲁⲩ","ⲕⲣⲓⲥⲓⲥ","ϩⲟⲧⲉ",
			  "ⲁⲛⲁⲥⲧⲁⲥⲓⲥ","ⲡⲁⲣⲟⲩⲥⲓⲁ","ⲙⲛⲧⲣⲱⲙⲉ","ϭⲓⲛⲱⲛⲁϩ","ⲙⲛⲧⲣⲉϥⲣϩⲟⲧⲉ","ϭⲓⲛⲛⲁⲩ","ϭⲓⲛⲥⲱⲧⲙ","ϭⲓⲛϣⲱⲗⲙ","ϭⲓⲛϣⲁϫⲉ","ⲉⲛⲉⲣⲅⲓⲁ","ⲕⲟⲗⲁⲥⲓⲥ","ⲩⲛⲟⲩ",
			  "ⲧⲁⲡⲣⲟ","ⲡⲟⲗⲓⲥ","ϩⲓⲏ","ⲡⲉ","ⲕⲱⲙⲏ","ⲕⲗⲟⲟⲗⲉ","ⲅⲉⲛⲉⲁ","ⲛⲁⲩ","ⲙⲛⲧⲕⲟⲩⲓ","ⲙⲛⲧⲁⲧⲛⲁϩⲧⲉ","ϭⲓϫ","ⲛⲏⲥⲧⲉⲓⲁ","ⲑⲁⲗⲁⲥⲥⲁ","ⲅⲉϩⲉⲛⲛⲁ","ⲥⲁⲧⲉ",
			  "ⲟⲩⲉⲣⲏⲧⲉ","ⲙⲁⲣⲧⲩⲣⲓⲁ","ⲙⲛⲧϫⲱⲱⲣⲉ","ⲟⲩⲱⲧ","ⲏⲡⲉ","ⲥⲏϥⲉ","ⲁⲫⲟⲣⲙⲏ","ⲭⲣⲉⲓⲁ","ϣⲧⲏⲛ","ϣⲉⲉⲣⲉ","ⲩϣⲏ","ⲁⲑⲏⲧ","ⲁⲧⲥⲃⲱ","ⲉⲛⲧⲟⲗⲏ","ⲃⲗⲗⲏ",
			  "ⲡⲁϣⲉ","ϩⲉⲛⲉⲉⲧⲏ","ⲥⲩⲛⲁⲅⲱⲅⲏ","ⲙⲛⲧϫⲁⲥⲓϩⲏⲧ","ⲙⲛⲧⲃⲁⲃⲉⲣⲱⲙⲉ","ⲥⲃⲱ","ⲙⲛⲧⲣⲙⲛϩⲏⲧ","ⲡⲁⲛⲟⲩⲣⲅⲓⲁ","ⲙⲛⲧϩⲁⲡⲗⲟⲩⲥ","ⲃⲁϣⲟⲣ","ⲕⲁⲕⲓⲁ","ⲛⲟⲩⲛⲉ",
			  "ⲉϩⲉ","ⲁϭⲟⲗⲧⲉ","ⲁⲥⲟⲩ","ⲧⲓⲙⲏ","ϣⲃⲉⲓⲱ","ⲙⲛⲧϩⲏⲕⲉ","ⲙⲉ","ⲙⲛⲧⲁⲑⲏⲧ","ⲟⲓⲕⲟⲩⲙⲉⲛⲏ","ⲙⲛⲧϩⲙϩⲁⲗ","ⲱⲇⲏ","ϩⲉⲗⲡⲓⲥ","ⲭⲁⲣⲓⲥ","ⲉⲓⲣⲏⲛⲏ","ⲙⲛⲧⲙⲛⲧⲣⲉ",
			  "ⲕⲟⲓⲛⲱⲛⲓⲁ","ⲥⲟⲫⲓⲁ","ⲙⲛⲧⲥⲁⲃⲉ","ⲙⲛⲧⲥⲟϭ","ⲙⲛⲧϭⲱⲃ","ⲁⲛⲁⲅⲕⲏ","ⲁⲛⲟⲙⲓⲁ","ⲡⲁⲣⲣⲏⲥⲓⲁ","ⲡⲟⲛⲏⲣⲓⲁ","ⲙⲛⲧⲁⲅⲁⲑⲟⲥ","ⲙⲛⲧⲛⲟⲩⲧⲉ","ⲙⲛⲧⲁⲧⲛⲟⲩⲧⲉ","ⲣⲓ",
			  "ⲙⲛⲧⲥⲩⲛⲕⲗⲏⲧⲓⲕⲟⲥ","ⲙⲛⲧⲙⲟⲛⲁⲭⲟⲥ","ⲭⲱⲣⲁ","ⲁⲅⲉⲗⲏ","ϣⲱⲙⲉ","ⲇⲉⲕⲁⲡⲟⲗⲓⲥ","ϩⲟ","ⲡⲏⲅⲏ","ⲙⲁⲥⲧⲓⲅⲝ","ⲥϩⲓⲙⲉ","ⲡⲓⲥⲧⲓⲥ","ⲉⲝⲟⲩⲥⲓⲁ","ⲁⲡⲉ","ϩⲁⲗⲁⲥⲥⲁ","ⲡⲁⲣⲁⲇⲟⲥⲓⲥ",
			  "ⲁⲅⲟⲣⲁ","ⲡⲁⲣⲁⲃⲟⲗⲏ","ⲧⲣⲁⲡⲉⲍⲁ","ⲙⲣⲣⲉ","ⲥⲱϣⲉ","ⲇⲓⲕⲁⲓⲟⲥⲩⲛⲏ","ⲡⲁⲛϩⲟⲡⲗⲓⲁ","ⲁⲅⲁⲡⲏ","ⲙⲛⲧϩⲁⲣϣϩⲏⲧ","ϩⲩⲡⲟⲙⲟⲛⲏ","ⲙⲛⲧⲣⲙⲙⲁⲟ","ⲙⲛⲧⲡⲁⲣⲑⲉⲛⲟⲥ","ⲙⲛⲧϩⲏⲧ","ⲑⲗⲓⲯⲓⲥ"])
	noun_m = set(["ⲉⲓⲱⲧ","ⲥⲱⲙⲁ","ⲡⲛⲉⲩⲙⲁ","ⲣⲁⲛ","ϫⲟⲉⲓⲥ","ⲭⲣⲓⲥⲧⲟⲥ","ϩⲟⲟⲩ","ϣⲟⲩϣⲟⲩ","ⲟⲩⲱϣⲙ","ⲡⲁⲥⲭⲁ","ⲕⲟⲥⲙⲟⲥ","ⲛⲟⲩⲧⲉ","ⲡⲟⲛⲏⲣⲟⲥ","ⲃⲓⲟⲥ","ⲥⲟⲛ","ⲣⲱⲙⲉ","ⲃⲟⲗ","ⲣⲡⲉ","ⲁϩⲉ","ϣⲏⲣⲉ","ⲙⲁⲓⲣⲱⲙⲉ","ϣⲱⲛⲉ","ⲟⲩϫⲁⲓ","ⲁϣⲁⲓ","ⲛⲟϭⲛⲉϭ","ϣⲓⲡⲉ","ϩⲏⲧ","ϩⲗⲗⲟ","ϫⲡⲓⲟ","ⲙⲉⲉⲩⲉ","ⲙⲁ","ⲙⲧⲟⲛ","ⲙⲟⲧⲉ","ϭⲱⲛⲧ","ϣⲗⲏⲗ","ⲡⲓⲣⲁⲥⲙⲟⲥ","ⲡⲣⲉⲥⲃⲩⲧⲉⲣⲟⲥ","ⲁⲣⲭⲏⲉⲡⲓⲥⲕⲟⲡⲟⲥ","ϩⲟ","ϣⲁϫⲉ","ϫⲓϩⲣⲁϥ","ⲙⲏⲏϣⲉ","ⲟⲩⲉ","ⲉⲥⲏⲧ","ϫⲟⲉⲓ","ⲱⲃϣ","ⲑⲁⲃ","ⲃⲗⲗⲉ","ⲏⲓ","ⲃⲁⲡⲧⲓⲥⲧⲏⲥ","ⲟⲩⲟⲓ","ⲥⲧⲁⲩⲣⲟⲥ","ⲉⲩⲁⲅⲅⲉⲗⲓⲟⲛ","ⲉⲟⲟⲩ","ⲕⲁϩ","ⲙⲉⲣⲓⲧ","ⲧⲟⲟⲩ","ⲥⲁϩ","ⲕⲱϩⲧ","ⲙⲟⲟⲩ","ⲛⲟϭ","ⲃⲉⲕⲉ","ⲙⲁⲕϩ","ⲱⲛϩ","ⲃⲁⲗ","ϥⲛⲧ","ϩⲙⲟⲩ","ϩⲁⲅⲓⲟⲥ","ⲥⲧⲣⲁⲧⲏⲗⲁⲧⲏⲥ","ⲙⲁⲣⲧⲩⲣⲟⲥ","ϥⲁⲓⲕⲗⲟⲙ","ⲁⲅⲱⲛ","ⲉⲃⲟⲧ","ⲣⲣⲟ","ϣⲟⲣⲡ","ⲇⲓⲁⲃⲟⲗⲟⲥ","ⲙⲧⲟ","ⲥⲉⲉⲡⲉ","ⲣⲟ","ⲡⲁⲗⲗⲁϯⲟⲛ","ⲇⲓⲁⲧⲁⲅⲙⲁ","ϫⲣⲟ","ⲡⲟⲗⲉⲙⲟⲥ","ⲥⲧⲣⲁⲧⲉⲩⲙⲁ","ⲟⲣⲇⲓⲛⲟⲛ","ⲥⲧⲟⲓ","ⲗⲓⲃⲁⲛⲟⲥ","ϣⲟⲩϩⲏⲛⲉ","ϩⲟϫϩϫ","ⲛⲁⲩ","ⲁⲣⲓⲥⲧⲟⲛ","ⲧⲏⲣϥ","ⲙⲁⲕⲁⲣⲓⲟⲥ","ⲧⲃⲃⲟ","ⲅⲉⲛⲛⲁⲓⲟⲥ","ⲥⲁⲃⲃⲁⲧⲟⲛ","ⲕⲟⲙⲉⲥ","ϫⲓⲛϫⲏ","ⲡⲉⲧϩⲟⲟⲩ","ⲡⲉⲧⲛⲁⲛⲟⲩϥ","ⲃⲁⲣⲟⲥ","ϩⲟϥ","ⲡⲁⲣⲁⲇⲉⲓⲥⲟⲥ","ⲃⲟⲏⲑⲟⲥ","ⲥⲧⲉⲣⲉⲱⲙⲁ","ⲥⲟⲫⲟⲥ","ⲣⲙⲛϩⲏⲧ","ⲧⲱⲧ","ⲙⲟⲩⲓ","ⲧⲁⲉⲓⲟ","ⲥⲱϣ","ϣⲃⲣⲣϩⲱⲃ","ⲅⲣⲁⲙⲙⲁⲧⲉⲩⲥ","ϫⲱⲱⲙⲉ","ⲥⲱⲛⲧ","ⲟⲩⲟⲓⲉϣ","ⲱϩⲥ","ⲣⲏ","ⲟⲟϩ","ⲉⲙⲛⲧ","ⲓⲉⲣⲟ","ⲧⲱϩ","ⲟⲩⲱϣ","ⲙⲁⲥⲉ","ϩⲱⲃ","ⲕⲁⲓⲣⲟⲥ","ⲃⲁⲣⲃⲁⲣⲟⲥ","ⲥⲟⲃⲧⲉ","ⲣⲟⲟⲩϣ","ϩⲟⲩⲟ","ϫⲓⲛϭⲟⲛⲥ","ⲡⲁⲛⲧⲟⲕⲣⲁⲧⲱⲣ","ⲗⲁⲟⲥ","ϩⲁⲣϣϩⲏⲧ","ⲛⲁ","ⲁⲡⲟⲥⲧⲟⲗⲟⲥ","ϭⲱⲗⲡ","ⲧⲁϣⲉⲟⲉⲓϣ","ⲧⲱϩⲙ","ⲡⲛⲉⲩⲙⲁⲧⲓⲕⲟⲥ","ϩⲗⲗⲱ","ⲡⲣⲟⲫⲏⲧⲏⲥ","ϫⲁⲓⲉ","ⲟⲩⲟⲉⲓⲛ","ⲕⲁⲕⲉ","ϣⲁϩ","ϩⲏⲃⲥ","ϫⲁϫⲉ","ⲁⲅⲁⲑⲟⲥ","ⲣⲉϥⲣⲛⲟⲃⲉ","ⲁⲧⲛⲟⲩⲧⲉ","ⲛⲟⲃⲉ","ⲙⲁⲓⲛⲟⲩⲧⲉ","ⲥⲛⲟϥ","ⲙⲟⲛⲁⲭⲟⲥ","ⲕⲣⲟ","ⲟⲩⲱ","ⲁⲣⲭⲓⲥⲩⲛⲁⲅⲱⲅⲟⲥ","ϩⲁⲙϣⲉ","ϣⲟⲉⲓϣ","ϣⲧⲉⲕⲟ","ϩⲟⲩⲙⲓⲥⲉ","ⲡⲓⲛⲁⲝ","ⲟⲩⲟⲓ","ⲭⲟⲣⲧⲟⲥ","ⲧⲃⲧ","ⲧⲏⲩ","ⲧⲟⲡ","ⲟⲉⲓⲕ","ⲇⲁⲓⲙⲱⲛⲓⲟⲛ","ϭⲗⲟϭ","ⲗⲁⲥ","ⲥⲟⲉⲓⲧ","ⲟⲩⲟⲧⲟⲩⲉⲧ","ϩⲓⲥⲉ","ⲕⲁⲣⲡⲟⲥ","ⲕⲉ","ⲙⲓϣⲉ","ⲥⲙⲟⲧ","ⲧⲱϣ","ϩⲁⲣⲉϩ","ϫⲓⲟⲩⲉ","ϯⲧⲱⲛ","ⲕⲱϩ","ⲙⲟⲥⲧⲉ","ⲕⲣⲟϥ","ϭⲙ","ϣⲓⲛⲉ","ⲃⲓⲣ"])
	noun_pl = set(["ⲉⲣⲏⲩ",
			   "ⲁⲧⲑⲁⲃ","ⲣⲉϥⲧⲱⲣⲡ","ⲣⲉϥϣⲙϣⲉⲉⲓⲇⲱⲗⲟⲛ","ⲣⲉϥⲥⲁϩⲟⲩ","ⲣⲉϥϯϩⲉ","ⲣⲉϥϫⲓ","ⲕⲟⲩⲓ","ⲁⲅⲅⲉⲗⲟⲥ","ϩⲱⲃ","ⲁⲡⲓⲥⲧⲟⲥ","ⲥⲛⲏⲩ","ϭⲓⲛⲟⲩⲟⲟⲙ","ⲕⲟⲟⲩⲉ","ⲥⲱⲙⲁ","ϣⲁϫⲉ",
			   "ⲯⲩⲭⲟⲟⲩⲉ","ⲣⲱⲙⲉ","ⲉⲥⲑⲏⲧⲏⲣⲓⲟⲛ","ⲃⲁⲗ","ϩⲟⲟⲩ","ⲙⲁⲑⲏⲧⲏⲥ","ⲟⲉⲓⲕ","ⲧⲃⲧ","ⲗⲁⲕⲙ","ⲥⲁ","ⲫⲁⲣⲓⲥⲥⲁⲓⲟⲥ","ⲙⲁⲁϫⲉ","ϣⲏⲛ","ⲕⲱⲙⲏ","ⲡⲣⲟⲫⲏⲧⲏⲥ","ⲡⲣⲉⲥⲃⲩⲧⲉⲣⲟⲥ","ⲁⲣⲭⲓⲉⲣⲉⲩⲥ",
			   "ⲅⲣⲁⲙⲙⲁⲧⲉⲩⲥ","ⲣⲉϥⲣⲛⲟⲃⲉ","ϩⲟⲓⲧⲉ","ⲟⲃϩⲉ","ϣⲏⲣⲉ","ⲥⲙⲟⲩ","ⲉⲓⲇⲱⲗⲟⲛ","ϣⲉ","ⲱⲛⲉ","ⲙⲟⲩⲛⲅ","ⲛⲟⲩⲧⲉ","ⲥⲩⲛⲕⲗⲓϯⲕⲟⲥ","ⲉⲛⲧⲟⲗⲏ","ⲩϣⲟⲟⲩⲉ","ⲭⲣⲓⲥϯⲁⲛⲟⲥ","ϩⲙϩⲁⲗ",
			   "ⲉⲩⲁⲅⲅⲉⲗⲓⲟⲛ","ⲛⲟϭ","ⲉⲓⲟⲧⲉ","ⲣⲟⲙⲡⲉ","ⲥⲩⲛⲁⲝⲓⲥ","ϩⲃⲏⲩⲉ","ϩⲓⲥⲉ","ⲉⲥⲟⲟⲩ","ϫⲓⲟⲩⲉ","ϯⲧⲱⲛ","ⲃⲗⲗⲉ","ⲥⲡⲟⲧⲟⲩ","ⲃⲟⲗ","ϩⲏⲧ","ϣⲟϫⲛⲉ","ⲥⲕⲉⲡⲁⲥⲧⲏⲥ","ϩⲗⲗⲟⲓ","ϩⲣⲟⲟⲩ",
			   "ⲭⲣⲉⲓⲥⲧⲓⲁⲛⲟⲥ","ⲟⲩⲉϭⲣⲟ","ⲭⲁⲣⲧⲏⲥ","ⲙⲏⲙⲟⲟⲩ","ϣⲟϣⲟⲩ","ⲉⲡⲓⲥⲧⲟⲗⲏ","ⲥⲉⲗⲓⲥ","ϫⲃⲃⲉⲥ","ⲇⲁⲓⲙⲱⲛ","ⲙⲏⲏϣⲉ","ⲁϩⲟ","ⲣⲉϥϯ","ϩⲏⲕⲉ","ⲣⲣⲱⲟⲩ","ⲛⲟⲃⲉ","ϭⲟⲗ","ϫⲓ","ⲟⲩⲁ",
			   "ϩⲓⲟⲟⲩⲉ","ⲣⲓⲣ","ⲏⲓ","ϩⲉⲗⲗⲏⲛ","ⲙⲁⲅⲉⲓⲣⲟⲥ","ⲥⲓⲟⲩ","ⲥⲟⲃⲧ","ⲙⲁ","ⲉⲩⲣⲓⲡⲟⲥ","ⲙⲛⲧⲣⲉϥϫⲓⲛϭⲟⲛⲥ","ⲧⲟⲡⲟⲥ","ⲧⲃⲛⲟⲟⲩⲉ","ϭⲟⲟⲙ","ϫⲟⲓ","ⲡⲉⲧϩⲟⲟⲩ","ⲭⲏⲣⲁ","ϩⲗⲗⲟ",
			   "ϩⲗⲗⲱ","ⲟⲣⲫⲁⲛⲟⲥ","ϣⲙⲙⲟ","ϩⲟⲙⲧ","ⲉⲗⲁⲭⲓⲥⲧⲟⲛ","ⲕⲉⲉⲥ","ⲙⲁⲥⲉ","ⲉϩⲟⲟⲩ","ϩⲧⲟ","ⲉⲓⲱ","ⲉϫⲏⲩ","ⲃⲁⲣⲃⲁⲣⲟⲥ","ϩⲓⲟⲙⲉ","ⲁϭⲟⲗⲧⲉ","ϫⲓⲛϭⲟⲛⲥ","ⲥⲓⲟⲟⲩⲛⲉ","ⲉⲡⲟⲓⲕⲓⲟⲛ",
			   "ⲑⲗⲓⲯⲓⲥ","ⲕⲃⲁ","ⲏⲣⲡ","ϭⲟⲙ","ϩⲉⲑⲛⲟⲥ","ⲁⲧⲛⲟⲩⲧⲉ","ⲙⲛⲧⲁⲡⲟⲥⲧⲟⲥ","ⲙⲛⲧⲁⲕⲁⲑⲁⲣⲧⲟⲥ","ⲣⲉϥϫⲓⲛϭⲟⲛⲥ","ϭⲓϫ","ⲕⲁϩ","ⲁⲧⲛⲁ","ⲟⲩⲱϣ","ⲛⲏⲥⲧⲉⲓⲁ","ⲡⲟⲛⲏⲣⲟⲛ","ⲥⲟⲫⲟⲥ",
			   "ⲥⲁⲃⲉⲉⲩ","ⲓⲟⲩⲇⲁⲓ","ⲙⲁⲉⲓⲛ","ⲥⲟϭ","ϭⲱⲃ","ⲧⲃⲃⲟ","ⲥⲟⲫⲓⲁ","ⲡⲓⲥⲧⲓⲥ","ⲧⲉⲗⲉⲓⲟⲥ","ⲁⲣⲭⲱⲛ","ⲁⲓⲱⲛ","ϯⲥⲃⲱ","ϣⲱⲛⲃ","ⲡⲛⲉⲩⲙⲁⲧⲓⲕⲟⲛ","ⲡⲛⲉⲩⲙⲁⲧⲓⲕⲟⲥ","ⲕⲣⲟϥ","ⲇⲓⲕⲁⲓⲟⲛ",
			   "ⲥⲁϩⲟⲩ","ϣⲟⲣⲡ","ⲅⲣⲁⲫⲏ","ϩⲏⲃⲥ","ⲁⲧϩⲏⲧ","ⲙⲛⲧⲥⲟϭ","ⲛⲩⲕⲧⲉⲣⲓⲥ","ⲡⲁⲑⲟⲥ","ⲡⲉⲧⲟⲩⲁⲁⲃ","ϫⲓϫⲉⲉⲩⲉ","ⲙⲉⲉⲩⲉ","ϣⲧⲏⲛ","ⲧⲟⲉⲓⲥ","ⲥⲩⲛⲕⲗⲏⲧⲓⲕⲟⲥ","ⲭⲣⲏⲙⲁ","ⲅⲉⲣⲁⲥⲏⲛⲟⲥ",
			   "ⲙϩⲁⲟⲩ","ⲡⲁⲓⲇⲉⲥ","ϩⲁⲗⲩⲥⲓⲥ","ⲧⲟⲩⲓⲏ","ⲉϣⲁⲩ","ⲡⲛⲉⲩⲙⲁ","ⲁⲕⲁⲑⲁⲣⲧⲟⲛ","ⲥⲱϣⲉ","ϩⲟⲉⲓⲧⲉ","ⲧⲟϣ","ⲥⲱⲛⲉ","ⲥⲩⲅⲅⲉⲛⲏⲥ","ⲧⲙⲉ","ⲙⲟϫϩ","ⲥⲁⲛⲇⲁⲗⲓⲟⲛ","ⲟⲩⲉⲣⲏⲧⲉ","ⲙⲉⲅⲓⲥⲧⲁⲛⲟⲥ",
			   "ⲭⲓⲗⲓⲁⲣⲭⲟⲥ","ⲁⲛⲁⲩϣ","ⲁⲡⲟⲥⲧⲟⲗⲟⲥ","ϭⲗⲱϭ","ϣⲱⲛⲉ","ϯⲙⲉ","ⲡⲟⲗⲓⲥ","ⲁⲅⲟⲣⲁ","ⲁⲡⲟⲧ","ⲝⲉⲥⲧⲏⲥ","ⲭⲁⲗⲕⲓⲛ","ϩⲩⲡⲟⲕⲣⲓⲧⲏⲥ","ⲥⲃⲟⲟⲩⲉ","ⲡⲟⲣⲛⲉⲓⲁ","ϩⲱⲧⲃ","ⲙⲛⲧⲛⲟⲉⲓⲕ",
			   "ⲙⲛⲧⲙⲁⲓ","ⲡⲟⲛⲏⲣⲓⲁ","ⲩϩⲟⲟⲣ","ⲥⲣⲉϥⲣⲓϥⲉ","ⲧⲏⲏⲃⲉ","ⲙⲡⲟ","ⲥⲩⲛⲁⲅⲱⲅⲏ","ⲟⲩⲟⲉⲓⲛ","ϩⲟⲩⲟ","ϣⲗⲟϥ","ⲁⲣⲭⲏ","ⲉⲝⲟⲩⲥⲓⲁ","ⲕⲟⲥⲙⲟⲕⲣⲁⲧⲱⲣ","ⲕⲟⲧⲥ","ⲡⲣⲁⲝⲓⲥ","ϩⲩⲡⲁⲣⲭⲟⲛⲧⲁ",
			   "ⲗⲏⲥⲧⲏⲥ","ϣⲗⲏⲗ","ⲙⲁⲣⲅⲁⲣⲓⲧⲏⲥ","ⲥⲟⲩⲟ","ϣⲟⲛⲧⲉ","ⲕⲗⲏⲣⲟⲥ","ⲃⲟⲩϩⲉ"])

	# Verbs
	verbs = set(["ⲥⲱⲧⲙ","ϫⲓ","ⲣϩⲏⲃⲉ","ϥⲓ","ⲉⲓⲣⲉ","ⲟⲩⲱ","ⲕⲣⲓⲛⲉ","ⲥⲱⲟⲩϩ","ϯ","ⲧⲁⲕⲟ","ⲟⲩϫⲁⲓ","ⲥⲟⲟⲩⲛ","ϣⲱⲡⲉ","ϣⲱⲱⲧ","ⲣϣⲁ","ⲥϩⲁⲓ","ⲧⲱϩ","ϫⲱ","ϣϣⲉ","ⲉⲓ","ⲙⲟⲩⲧⲉ","ⲟⲩⲱⲙ","ⲧⲟⲗⲙⲁ","ϫⲓϩⲁⲡ","ⲙⲡϣⲁ","ⲡⲱϩ","ϣⲓⲡⲉ","ϣ","ϭⲙϭⲟⲙ","ⲇⲓⲁⲕⲣⲓⲛⲉ","ϥⲉϭ","ϥⲱϭⲉ","ⲕⲗⲏⲣⲟⲛⲟⲙⲉⲓ","ⲡⲗⲁⲛⲁ","ϫⲉⲕⲙ","ⲧⲃⲃⲟ","ⲧⲙⲁⲉⲓⲟ","ⲉⲝⲉⲥⲧⲉⲓ","ⲣⲛⲟϥⲣⲉ","ⲕⲁ","ⲣϫⲟⲉⲓⲥ","ⲟⲩⲟⲥϥ","ⲧⲟⲩⲛⲉⲥ","ⲧⲟⲩⲛⲟⲥ","ⲁⲁ","ⲧⲱϭⲉ","ⲡⲱⲧ","ⲡⲟⲣⲛⲉⲩⲉ","ⲣⲛⲟⲃⲉ","ϫⲓⲧ","ϣⲉⲡ","ϯⲉⲟⲟⲩ","ⲟⲩⲱϣ","ⲧⲟⲩϫⲉ","ϩⲓⲥⲉ","ϣⲱϣⲧ","ϣϭⲙϭⲟⲙ","ⲕⲁⲁ","ⲃⲱⲕ","ⲣⲙⲟⲛⲁⲭⲟⲥ","ϫⲉ","ⲙⲟⲩ","ϣⲱⲛⲉ","ⲧⲟⲣⲡ","ϭⲓⲛⲉ","ⲛⲁⲩ","ⲡⲱϣⲥ","ⲟⲩⲉϣ","ⲥⲟⲧⲙ","ⲁϩⲉ","ⲗⲟϭ","ϩⲙⲟⲟⲥ","ⲫⲣⲟⲛⲧⲓⲍⲉ","ⲣⲓⲙⲉ","ⲡⲁⲣⲁⲕⲁⲗⲉⲓ","ϯⲙⲧⲟⲛ","ϣⲱϭⲉ","ⲥⲗⲥⲱⲗ","ⲧⲱⲟⲩⲛ","ϫⲟⲟ","ⲉϣ","ⲥⲧⲱⲧ","ⲟⲩⲱⲛϩ","ⲙⲉⲉⲩⲉ","ϯⲗⲟⲅⲟⲥ","ϣⲁⲧ","ϫⲛⲉ","ⲣϩⲟⲧⲉ","ⲁⲙⲁϩⲧⲉ","ϫⲡⲟ","ϫⲡⲓⲉ","ⲁⲡⲁⲛⲧⲁ","ⲙⲟⲩⲛ","ⲣ","ⲧⲟϭ","ϣⲱⲱⲡⲉ","ⲕⲱⲧⲉ","ⲟⲩⲱϣⲃ","ⲉⲓⲱⲣϩ","ϩⲉⲗⲡⲓⲍⲉ","ⲉⲓⲉⲣϩ","ⲙⲟⲩϩ","ϭⲱ","ϩⲗⲟⲡⲗⲡ","ⲕⲓⲙ","ⲁⲓⲧⲉⲓ","ⲡⲁⲣⲁⲅⲉ","ⲗⲟ","ⲕⲧⲟ","ϫⲛⲟⲩ","ⲧⲁϫⲣⲟ","ϩⲁⲣⲉϩ","ⲟⲩⲟⲙ","ϣⲛ","ⲡⲣⲟⲥⲕⲁⲣⲧⲉⲣⲉⲓ","ⲥⲱϣⲙ","ⲧⲥⲓⲉ","ϩⲱⲛ","ⲛⲟϫ","ϣⲡϩⲙⲟⲧ","ⲡⲟϣ","ⲧⲁⲁ","ⲥⲙⲟⲩ","ⲟⲩⲉϩⲥⲁϩⲛⲉ","ⲥⲉⲓ","ⲣϩⲟⲩⲟ","ⲁⲗⲉ","ϫⲟⲉⲓ","ⲁⲣⲭⲉⲓ","ϯⲧⲱⲛ","ⲡⲉⲓⲣⲁⲍⲉ","ⲁϣⲁϩⲟⲙ","ϯⲙⲁⲉⲓⲛ","ⲧⲁⲗⲉ","ϫⲓⲟⲉⲓⲕ","ϭⲱϣⲧ","ⲙⲉⲕⲙⲟⲩⲕ","ⲉⲓⲙⲉ","ⲙⲟⲕⲙⲉⲕ","ⲛⲟⲉⲓ","ⲡⲉϣ","ⲙⲉϩ","ⲡⲱϣ","ⲉⲓⲛⲉ","ⲥⲉⲡⲥⲱⲡ","ϫⲱϩ","ⲛⲧ","ⲛⲉϫ","ⲙⲟⲟϣⲉ","ⲥⲱⲧϥ","ϫⲟⲟⲩ","ⲉⲡⲓⲧⲓⲙⲁ","ⲧⲟⲩⲛ","ϫⲡⲓ","ⲥⲧⲟ","ⲙⲟⲟⲩⲧ","ⲟⲩⲁϩ","ⲁⲣⲛⲁ","ⲛⲁϩⲙ","ⲥⲟⲣⲙ","ⲥⲱⲣⲙ","ⲧⲟⲩϫⲟ","ϯϩⲏⲩ","ϫⲡⲉ","ϯⲟⲥⲉ","ϯϣⲓⲡⲉ","ϫⲓϯⲡⲉ","ϣⲃⲧ","ⲟⲩⲃⲁϣ","ⲧⲱϭⲥ","ⲡⲓⲣⲉ","ϣⲁϫⲉ","ⲧⲁⲙⲓⲟ","ⲡⲱⲣϣ","ⲧⲁⲩⲉ","ϫⲉⲕ","ⲥⲟϣ","ⲟⲩⲁϣ","ϣⲧⲟⲣⲧⲣ","ⲁⲥⲡⲁⲍⲉ","ⲛ","ⲧⲁϩⲟ","ⲣⲁϩⲧ","ⲧⲁⲩⲉⲥϩⲃⲏⲓⲧⲉ","ϩⲣⲁϫⲣⲉϫ","ⲧⲱⲥ","ⲁⲛⲉⲭⲉ","ϩⲉ","ϩⲓⲧⲉ","ⲧⲁⲩⲉⲥϩⲃⲏⲏⲧⲉ","ⲃⲟⲏⲑⲉⲓ","ϣⲁⲁ","ⲡⲓⲥⲧⲉⲩⲉ","ϫⲓϣⲕⲁⲕ","ⲕⲟⲧ","ϣⲗⲏⲗ","ⲧⲥⲁⲃⲟ","ⲙⲟⲩⲟⲩⲧ","ⲣⲛⲟϭ","ⲣⲕⲟⲩⲉⲓ","ⲇⲓⲁⲕⲟⲛⲓ","ⲕⲧⲉ","ϣⲱⲡ","ϣⲟⲡ","ⲧⲛⲛⲟⲟⲩ","ⲕⲱⲗⲩ","ⲧⲥⲉ","ⲥⲕⲁⲛⲇⲁⲗⲓⲍⲉ","ϣⲁⲁⲧ","ϫⲉⲛⲁ","ϭⲁⲗⲉ","ⲡⲟⲣⲕ","ϫⲟⲕⲣ","ⲃⲁⲁⲃⲉ","ⲕⲁϩⲙⲟⲩ","ⲣⲉⲓⲣⲏⲛⲏ","ϫⲱⲕ","ⲙⲉϣϣⲉ","ϣⲙϣⲉ","ⲕⲱ","ⲥⲩⲙⲃⲟⲩⲗⲉⲩⲉ","ϯⲣⲁⲛ","ⲕⲉⲗⲉⲩⲉ","ϯⲙⲉⲉⲩⲉ","ϯϭⲟⲙ","ϣⲟⲣⲡ","ⲑⲩⲥⲓⲁⲍⲉ","ⲕⲁⲧⲁⲡⲟⲛϯⲍⲉ","ⲛⲟⲉⲓⲛ","ⲣⲁⲡⲟⲡⲛⲓⲅⲉ","ⲧⲁⲗⲟ","ϩⲣⲟⲕⲉⲩⲉ","ⲥⲱ","ⲧⲁⲙⲓⲉ","ⲁⲛⲁⲭⲱⲣⲉⲓ","ⲱϣ","ⲙⲉⲥⲧⲉ","ⲥⲉⲏⲣⲡ","ⲟⲩⲉⲙ","ⲧⲟⲃⲧⲃ","ϣⲟⲩϣⲟⲩ","ⲱⲣⲕ","ⲇⲓⲁⲕⲟⲛⲉⲓ","ⲧⲁⲙⲉ","ⲥⲙⲛⲧ","ⲡⲗⲉⲁ","ⲡⲉⲓⲑⲉ","ⲙⲉ","ⲛⲕⲟⲧⲕ","ⲛⲏⲥⲧⲉⲩⲉ","ⲧⲁⲓⲉ","ⲥⲁⲛⲟⲩϣ","ⲥⲱϣ","ⲧϭⲁⲓⲉ","ⲫⲑⲟⲛⲉⲓ","ⲧⲁⲕⲉ","ⲡⲱⲱⲛⲉ","ⲥⲣⲙⲣⲱⲙ","ⲙⲓϣⲉ","ⲕⲁⲣⲱⲙⲉ","ϩⲟⲟⲩϣ","ϫⲓϭⲟⲗ","ⲡⲁⲣⲁⲃⲁ","ϣⲓⲛⲉ","ⲣⲭⲣⲉⲓⲁ","ⲧⲥⲧⲟ","ⲧⲁⲙⲟ","ϫⲟⲡϫⲡ","ϫⲓⲧⲉ","ⲑⲙⲕⲟ","ⲗⲩⲡⲉⲓ","ⲙⲕⲁϩ","ϫⲉⲙⲉ","ⲧⲁⲓⲟ","ⲣⲕⲁⲕⲉ","ⲕⲁⲧⲁⲫⲣⲟⲛⲉⲓ","ⲙⲉⲣⲉ","ⲙⲉⲗⲉⲧⲁ","ⲃⲟⲟⲛⲉ","ϩⲟⲙⲟⲗⲟⲅⲉⲓ","ⲕⲁⲉⲡⲓⲥⲧⲏⲙⲏ","ⲉⲝⲁⲡⲁⲧⲁ","ϯⲥⲟ","ⲕⲁⲙⲁ","ⲙⲧⲟⲛ","ⲧⲁⲩⲟⲩⲟ","ϩⲉⲡ","ⲧⲱⲧ","ⲁϣϣⲕⲁⲕ","ⲧⲣⲣⲉ","ⲣⲱϣⲉ","ⲡⲁⲣⲁⲓⲧⲉⲓ","ⲙⲟⲩⲣ","ⲟⲩⲱϭⲡ","ⲡⲁϩ","ϫⲉⲣⲟ","ϫⲓϩⲛⲁⲩ","ϭⲱⲗⲡ","ⲉⲣ","ⲣⲁϣⲉ","ⲟⲩⲱϣⲧ","ⲥⲱⲛⲧ","ⲉⲡⲓⲕⲁⲗⲉⲓ","ⲡⲱⲛⲅ","ⲥⲱⲟⲩϩⲛⲁⲩ","ⲧⲱⲣⲡ","ⲡⲟⲛⲏⲣⲉⲩⲉ","ⲕⲁϫⲣⲟⲡ","ⲣϭⲣⲱϩ","ⲣⲣⲙⲙⲁⲟ","ⲥϭⲏⲣ","ϫⲟ","ⲱⲗ","ⲉϣϣⲉ","ϫⲓⲟⲩⲁ","ⲃⲟⲗⲃⲗ","ⲕⲟⲛⲥ","ⲡⲁⲣⲁⲇⲓⲅⲙⲁⲧⲓⲍⲉ","ⲣϩⲱⲃ","ⲧⲣⲩⲫⲁ","ⲁⲡⲁⲧⲁ","ⲙⲉϣⲧ","ϭⲛⲉⲓⲇⲱⲗⲟⲛ","ⲙⲟϣⲧ","ϭⲛ","ϥⲓⲧ","ϩⲱⲡ","ⲕⲱⲧ","ⲟⲩⲱⲧⲛ","ϩⲱ","ⲑⲗⲓⲃⲉ","ϭⲟⲧⲡ","ⲁⲛⲁⲅⲕⲁⲍⲉ","ⲥⲣϥⲉ","ⲙⲟⲛⲕ","ⲛⲟⲩϫⲉ","ⲉϣⲗⲟⲩⲗⲁⲓ","ⲣⲥⲧ","ⲣϣⲁⲩ","ⲥⲟⲣ","ϣⲓⲧⲉ","ⲥⲉⲩϩ","ⲉⲡⲓⲑⲩⲙⲉⲓ","ⲥⲟⲟⲩϩ","ⲣⲟⲉⲓⲥ","ⲧϩⲛⲉⲣⲱⲙⲉ","ⲟⲩⲱϩ","ϣⲁⲧⲟⲩ","ⲟⲩⲉϣϫⲱⲕⲙ","ⲣⲙⲛⲧⲣⲉ","ϫⲱⲕⲙ","ⲣⲕⲃⲁ","ⲕⲉⲧ","ⲁⲡⲉⲓⲗⲉⲓ","ⲥⲟⲧ","ⲥⲟⲩⲱⲛ","ⲧⲱⲙ","ⲣϩⲙϩⲁⲗ","ⲥⲱⲧⲉ","ⲛⲟⲩϭⲥ","ⲧⲁⲩⲟ","ⲉⲣⲏⲧ","ⲧⲁϫⲣⲉ","ⲧⲉϩⲙ","ⲥⲧⲁⲩⲣⲟⲩ","ϫⲓⲃⲁⲡⲧⲓⲥⲙⲁ","ⲃⲁⲡⲧⲓⲍⲉ","ⲉⲩⲁⲅⲅⲉⲗⲓⲍⲉ","ⲁⲑⲉⲧⲉⲓ","ⲥⲟⲩⲛ","ⲣϩⲛⲁ","ⲧⲁϣⲉⲟⲉⲓϣ","ⲧⲁϩⲙ","ⲥⲟⲧⲡ","ϫⲱⲱⲣⲉ","ⲕⲁⲧⲁⲣⲅⲉⲓ","ϫⲓⲥⲉ","ⲟⲩⲱⲥϥ","ⲡⲟⲣϫ","ⲥⲃⲧⲱⲧ","ϭⲟⲗⲡ","ϩⲟⲧϩⲧ","ⲭⲁⲣⲓⲍⲉ","ϯⲥⲃⲱ","ⲁⲛⲁⲕⲣⲓⲛⲉ","ⲧⲥⲉⲃⲉ","ⲣⲙⲏ","ⲣϩⲁϩ","ⲥⲣ","ⲧⲱϣ","ⲡⲱⲣϫ","ϣⲱⲗ","ϩⲟϫϩϫ","ⲟⲩⲉ","ⲱⲟⲟⲡ","ϫⲱϩⲙ","ϫⲓⲟⲩⲉ","ⲥⲁϩ","ⲧⲁⲙⲱ","ⲧⲛⲧⲱⲛ","ϫⲉⲣⲱ","ⲣⲱϩⲧ","ϣⲟⲕϩ","ⲛⲟⲩϫ","ⲣⲟⲩⲟⲉⲓⲛ","ϫⲓϫⲣⲟⲡ","ϩⲕⲟ","ⲉⲓⲃⲉ","ⲧⲱⲱⲃⲉ","ϫⲡⲓⲟ","ⲙⲉⲧⲁⲛⲟⲉⲓ","ⲟⲩⲁϩⲙⲉ","ⲙⲉⲣⲓⲧ","ⲥⲁϩⲟⲩ","ⲫⲟⲣⲉⲓ","ϯⲛⲧⲟⲗⲏ","ⲁⲡⲟⲧⲁⲥⲥⲉ","ⲑⲃⲃⲓⲟ","ⲥⲟⲣⲙⲉ","ⲫⲱϭⲉ","ⲧⲱⲙⲛⲧ","ⲙⲟⲣ","ⲥⲗⲡ","ⲟⲩⲉϭⲡ","ϩⲓⲟⲩⲉ","ⲡⲁϩⲧ","ⲃⲁⲥⲁⲛⲓⲍⲉ","ⲣⲛⲧ","ϫⲕϩⲁϩ","ⲙⲟⲟⲛⲉ","ⲧⲁⲟⲩⲟ","ⲛⲁ","ⲁⲣⲭⲉⲥⲑⲁⲓ","ⲣϣⲡⲏⲣⲉ","ϫⲓⲟⲟⲣ","ⲉⲗⲟ","ϣⲟⲩⲟ","ⲟϣ","ⲕⲧⲉⲓⲁⲧ","ⲣⲡⲁⲓ","ⲛⲁϩⲙⲉ","ϯϩⲟⲓ","ⲟⲩⲛⲣⲟ","ⲥⲱⲃⲉ","ⲧⲙⲙⲟ","ⲧⲁⲗϭⲟ","ⲛⲟⲩϩⲉ","ⲕⲏⲣⲩⲥⲥⲉ","ⲧⲁϩⲥ","ϯⲥⲟⲉⲓⲧ","ϯⲃⲁⲡⲧⲓⲥⲙⲁ","ⲉⲛⲉⲣⲅⲉⲓ","ⲧⲙⲁⲓⲟ","ⲡⲓⲑⲉ","ⲟⲣⲭⲉ","ⲣϣⲟⲣⲡ","ϣⲉ","ⲧⲟⲟⲩ","ⲟⲩⲉⲧⲟⲩⲱⲧ","ⲡⲉϣⲛⲟⲉⲓⲕ","ⲥⲓ","ⲕⲣⲟ","ⲙⲏⲏϣⲉ","ⲁⲡⲟⲥⲧⲁⲥⲥⲉ","ⲉⲓⲟⲣϩ","ⲧⲱⲕ","ⲡⲉ","ⲉⲓⲁ","ⲓⲁ","ϭⲉϣϭⲱϣ","ϩⲟⲣⲡ","ⲡⲣⲟⲫⲏⲧⲉⲩⲉ","ⲁⲑⲉⲧⲓ","ϫⲁϩⲙⲉ","ⲕⲁⲑⲁⲣⲓⲍⲉ","ϫⲁϩⲙ","ⲛⲉϫⲧⲁϥ","ⲟⲩⲱⲛ","ⲧⲉ","ϣⲡϩⲓⲥⲉ","ⲇⲟⲅⲙⲁⲧⲓⲍⲉ","ϭⲗⲟⲙⲗⲙ","ⲇⲟⲕⲓⲙⲁⲍⲉ","ⲕⲟⲓⲛⲱⲛⲉⲓ","ϭⲛⲁⲣⲓⲕⲉ","ϫⲓⲥⲃⲱ","ⲟⲩⲉϩ","ⲥⲡⲟⲩⲇⲁⲍⲉ","ⲉⲡⲓⲃⲟⲩⲗⲉⲩⲉ","ⲕⲣⲙⲣⲙ","ⲕⲁⲧⲁⲗⲁⲗⲉⲓ","ⲙⲟⲥⲧⲉ","ⲣⲛⲟⲉⲓⲧ","ⲱϩⲥ","ⲣⲙⲡϣⲁ","ϭⲱⲧϩ","ϭⲛⲭⲣⲏⲙⲁ","ⲟⲃϣ","ϭⲛⲧ","ϣⲉⲉⲓ","ϯϩⲓⲛⲏⲃ","ⲣⲉⲕⲣⲓⲕⲉ","ⲥⲙⲛ","ϫⲉϩⲙ"])

	# Updates from copt_lemma_lex.tab
	tt_lex = io.open(data_dir + "copt_lemma_lex.tab",encoding="utf8").read().strip().split("\n")
	tt_lex_verbs = [line.split("\t")[0] for line in tt_lex if line.split("\t")[1]=="V" if line.split("\t")[0] not in forbidden]
	for v in tt_lex_verbs:
		verbs.add(v)

	stative = set([])
	tt_lex = io.open(data_dir + "copt_lemma_lex.tab",encoding="utf8").read().strip().split("\n")
	tt_lex_stative = [line.split("\t")[0] for line in tt_lex if line.split("\t")[1]=="VSTAT" if line.split("\t")[0] not in forbidden]
	for v in tt_lex_stative:
		stative.add(v)
	stative = {k:k for k in stative}

	# Known foreign words from lang_lexicon.tab
	foreign_lex = io.open(data_dir + "lang_lexicon.tab",encoding="utf8").read().strip().split("\n")
	foreign = [line.split("\t")[0] for line in foreign_lex if not "*" in line]

	tt_lex_nouns = [line.split("\t")[0] for line in tt_lex if line.split("\t")[1]=="N" and line.split("\t")[0] not in forbidden]
	for n in tt_lex_nouns:
		if n in foreign:
			if n not in noun_m and (n.endswith("ⲁ") or n.endswith("ⲏ") or n.endswith("ⲥⲓⲥ")):
				noun_f.add(n)
			elif n not in noun_f:
				noun_m.add(n)
		else:
			if n not in noun_f and n not in verbs:
				noun_m.add(n)

	# Proper names
	names = set([])
	tt_lex_names = [line.split("\t")[0] for line in tt_lex if line.split("\t")[1]=="NPROP" if line.split("\t")[0] not in forbidden]
	for n in tt_lex_names:
		names.add(n)
	names = {n:n for n in names}

	forbidden_adv = ["ⲉⲧⲉⲓ","ⲉⲓⲙⲏⲧⲉⲓ"]  # Remove unnormalized ADVs if found in tt_lex
	tt_lex_advs = [line.split("\t")[0] for line in tt_lex if line.split("\t")[1] in ["ADV","CONJ"] and line.split("\t")[0] not in forbidden]
	adv = set([])
	for a in tt_lex_advs:
		if a not in noun_f and a not in noun_m and a not in verbs and a not in forbidden_adv:
			adv.add(a)
	adv = {k:k for k in adv}

	# Dictionary-ify
	noun_f = {k:k for k in noun_f}
	noun_m = {k:k for k in noun_m}
	noun_pl_no_v = {k:k for k in noun_pl if k not in verbs}  # Prohibit verbs to prevent squished possessives looking like conjunctives: nfjioue != nefjioue
	noun_pl = {k:k for k in noun_pl}
	prep = {k:re.sub(r'\(.*\)','',k) for k in prep}
	prep_m = {k:k for k in prep_m}  # Labial assimilated prepositions
	verbs = {k:k for k in verbs}

	immutable_verbs = ["ϫⲉⲓ"]  # Forms that verbs should *not* be mutated into, e.g. ji -> jei
	immutable_verbs = {k:k for k in immutable_verbs}

	verbs = mutate(r'([^ⲉ]|^)ⲓ',r'\1ⲉⲓ',verbs,{k:v for k,v in verbs.items()},exclude=dict(list(noun_f.items())+list(noun_m.items())+list(immutable_verbs.items())))
	adv = mutate(r'([^ⲉ]|^)ⲓ',r'\1ⲉⲓ',adv,{k:v for k,v in adv.items()},exclude=dict(list(noun_f.items())+list(noun_m.items())+list(verbs.items())))

	noun_f.update({"ϭⲓⲛ"+v:"ϭⲓⲛ"+v for v in verbs if not v.startswith("ϭⲓⲛ") and v not in foreign})
	noun_f.update({"ⲙⲛⲧ"+v:"ⲙⲛⲧ"+v for v in verbs if v not in foreign})
	noun_m.update({"ⲣⲉϥ"+v:"ⲣⲉϥ"+v for v in verbs if v not in foreign})
	noun_m.update({"ⲣϥ"+v:"ⲣⲉϥ"+v for v in verbs if v not in foreign})

	foreign_nouns = {n:n for n in dict(list(noun_m.items())+list(noun_f.items())) if n in foreign and n not in verbs}
	foreign_verbs = {v:v for v in verbs if v in foreign and v not in noun_m and v not in noun_f}
	foreign_adv = {a:a for a in adv if a in foreign}

	noun_m = mutate(r'([^ⲉ]|^)ⲓ',r'\1ⲏ',{k:v for k,v in foreign_nouns.items() if not (k.endswith("ⲁ") or k.endswith("ⲏ") or k.endswith("ⲥⲓⲥ"))},noun_m,exclude=dict(list(noun_f.items())+list(verbs.items())))
	noun_m = mutate(r'ⲉⲓ','ⲏ',{k:v for k,v in foreign_nouns.items() if not ((k.endswith("ⲁ") or k.endswith("ⲏ") or k.endswith("ⲥⲓⲥ")) or k.endswith("ⲏ"))},noun_m,exclude=dict(list(noun_f.items())+list(verbs.items())))
	noun_f = mutate(r'([^ⲉ]|^)ⲓ',r'\1ⲏ',{k:v for k,v in foreign_nouns.items() if (k.endswith("ⲁ") or k.endswith("ⲏ") or k.endswith("ⲥⲓⲥ"))},noun_f,exclude=dict(list(noun_m.items())+list(verbs.items())))
	noun_f = mutate(r'ⲉⲓ','ⲏ',{k:v for k,v in foreign_nouns.items() if (k.endswith("ⲁ") or k.endswith("ⲏ") or k.endswith("ⲥⲓⲥ"))},noun_f,exclude=dict(list(noun_m.items())+list(verbs.items())))

	# ei -> i only for foreign word, since this could be a diphthong in native words
	verbs = mutate(r'ⲉⲓ',r'ⲓ',foreign_verbs,verbs,exclude=dict(list(noun_m.items())+list(noun_f.items())+list(verbs.items())))
	noun_m = mutate(r'ⲉⲓ',r'ⲓ',{k:v for k,v in foreign_nouns.items() if not (k.endswith("ⲁ") or k.endswith("ⲏ") or k.endswith("ⲥⲓⲥ"))},noun_m,exclude=dict(list(noun_f.items())+list(verbs.items())))
	noun_f = mutate(r'ⲉⲓ',r'ⲓ',{k:v for k,v in foreign_nouns.items() if (k.endswith("ⲁ") or k.endswith("ⲏ") or k.endswith("ⲥⲓⲥ"))},noun_f,exclude=dict(list(noun_m.items())+list(verbs.items())))

	# g -> k only for foreign word
	noun_m = mutate(r'ⲅ',r'ⲕ',{k:v for k,v in foreign_nouns.items() if not (k.endswith("ⲁ") or k.endswith("ⲏ") or k.endswith("ⲥⲓⲥ"))},noun_m,exclude=dict(list(noun_f.items())+list(verbs.items())))
	noun_f = mutate(r'ⲅ',r'ⲕ',{k:v for k,v in foreign_nouns.items() if (k.endswith("ⲁ") or k.endswith("ⲏ") or k.endswith("ⲥⲓⲥ"))},noun_f,exclude=dict(list(noun_m.items())+list(verbs.items())))


	aberrant_noun_f = aberrant_noun_m = aberrant_noun_m_long = {}

	# TODO: deal with ref- prefix items

	aberrant_noun_m = mutate(r'([^ⲉ]|^)ⲓ',r'\1ⲉⲓ',noun_m,aberrant_noun_m,exclude=dict(list(verbs.items())+list(noun_f.items())))
	aberrant_noun_m = mutate(r'ⲟⲉⲓ',r'ⲟⲓ',noun_m,aberrant_noun_m,exclude=dict(list(verbs.items())+list(noun_f.items())))
	aberrant_noun_f = mutate(r'([^ⲉ]|^)ⲓ',r'\1ⲉⲓ',noun_f,aberrant_noun_f,exclude=dict(list(verbs.items())+list(noun_m.items())))

	aberrant_noun_f.update({"ⲙⲛⲧⲉⲣⲟ":"ⲙⲛⲧⲣⲣⲟ","ⲕⲕⲗⲏⲥⲓⲁ":"ⲉⲕⲕⲗⲏⲥⲓⲁ","ⲙⲛⲧⲙⲟⲛⲟⲭⲟⲥ":"ⲙⲛⲧⲙⲟⲛⲁⲭⲟⲥ"})
	aberrant_noun_m.update({"ⲉⲣⲟ":"ⲣⲣⲟ","ⲓⲏⲗ":"ⲓⲥⲣⲁⲏⲗ","ⲏⲉⲓ":"ⲏⲓ","ⲟⲩⲣⲏⲏⲧⲉ":"ⲟⲩⲉⲣⲏⲧⲉ","ϫⲥ":"ϫⲟⲉⲓⲥ","ⲉⲓⲉⲣⲟ":"ⲓⲉⲣⲟ","ⲙⲟⲛⲟⲭⲟⲥ":"ⲙⲟⲛⲁⲭⲟⲥ","ⲣⲁⲁⲧ":"ⲣⲁⲧ"})
	aberrant_noun_m.update({"ⲭⲣⲥ":"ⲭⲣⲓⲥⲧⲟⲥ","ⲭⲥ":"ⲭⲣⲓⲥⲧⲟⲥ"})

	names["ⲓⲥ"] = "ⲓⲏⲥⲟⲩⲥ"
	names.update({"ⲡⲁⲓ":"ⲡⲁⲓ","ⲧⲁⲓ":"ⲧⲁⲓ","ⲛⲁⲓ":"ⲛⲁⲓ"})  # Independent demonstratives work like names

	noun_not_verb = {k:v for k,v in dict(list(noun_m.items())+list(noun_f.items())+list(noun_pl.items())).items() if k not in verbs}

	conv_pos_m = [conv,ppos_m,noun_m]
	conv_pos_f = [conv,ppos_f,noun_f]
	conv_pos_pl = [conv,ppos_pl,noun_pl]

	aux_ei = {"ⲙⲡⲁⲧⲉⲓ":"ⲙⲡⲁⲧⲓ","ⲛⲧⲉⲣⲉⲓ":"ⲛⲧⲉⲣⲓ","ⲙⲡⲁϯ":"ⲙⲡⲁⲧⲓ","ϣⲁⲛϯ":"ϣⲁⲛⲧⲓ"}
	aux_ei_no_noun = {"ⲙⲡⲉⲓ":"ⲙⲡⲓ","ⲉⲧⲉⲓ":"ⲉⲧⲓ"}
	aux_ei_v = [aux_ei,verbs]
	v_not_n = {v:v for v in verbs if v not in noun_m and v not in forbidden}
	aux_ei_v_no_noun = [aux_ei_no_noun,v_not_n]

	noun_m.update(aberrant_noun_m)
	noun_f.update(aberrant_noun_f)
	#noun_pl.update(aberrant_noun_pl)

	h_noun_m = {k[1:]:v for k,v in noun_m.items() if initial(k,"ϩ")}
	h_noun_f = {k[1:]:v for k,v in noun_f.items() if initial(k,"ϩ")}
	h_verb = {k[1:]:v for k,v in verbs.items() if initial(k,"ϩ")}

	bi_subj = ["ϯ","ⲕ","ⲧⲉ","ϥ","ⲥ","ⲧⲛ","ⲧⲉⲧⲛ","ⲥⲉ","ⲧⲁ","ⲛⲧⲁ"]
	bi_subj = {k:k for k in bi_subj}
	# Fused tri bases that can work like bi_subj in the grammar:
	bi_subj["ⲛⲧⲉⲣⲉⲓ"]="ⲛⲧⲉⲣⲓ"
	bi_subj["ⲡⲉϯ"]="ⲡⲉⲧⲓ"
	bi_subj["ⲧⲉⲧⲉⲓ"]="ⲧⲉⲧⲓ"

	caus = {"ⲧⲣⲉ":"ⲧⲣⲉ","ⲧⲣ":"ⲧⲣⲉ"}
	inf_mark = {"ⲉ":"ⲉ","ⲙⲛⲛⲥⲁ":"ⲙⲛⲛⲥⲁ"}
	tri_aux = {"ⲁ":"ⲁ","ⲙⲉ":"ⲙⲉ","ⲙⲡ":"ⲙⲡ","ϣⲁ":"ϣⲁ"}
	tri_nom = {"ⲁ":"ⲁ","ⲙⲉⲣⲉ":"ⲙⲉⲣⲉ","ⲙⲡⲉ":"ⲙⲡⲉ","ϣⲁⲣⲉ":"ϣⲁⲣⲉ","ⲉⲣϣⲁⲛ":"ⲉⲣϣⲁⲛ","ⲣϣⲁⲛ":"ⲉⲣϣⲁⲛ","ⲟⲩⲛ":"ⲟⲩⲛ","ⲩⲛ":"ⲩⲛ","ⲙⲛ":"ⲙⲛ","ϣⲁⲛⲧⲉ":"ϣⲁⲛⲧⲉ"}
	tri_subj = {"ⲓ":"ⲓ","ⲕ":"ⲕ","ϥ":"ϥ","ⲥ":"ⲥ","ⲛ":"ⲛ","ⲧⲉⲧⲛ":"ⲧⲉⲧⲛ","ⲩ":"ⲩ","ⲟⲩ":"ⲟⲩ"}
	ppero = {"ⲓ":"ⲓ","ⲕ":"ⲕ","ϥ":"ϥ","ⲥ":"ⲥ","ⲛ":"ⲛ","ⲧⲉⲧⲛ":"ⲧⲉⲧⲛ","ⲩ":"ⲩ","ⲟⲩ":"ⲟⲩ","ⲧ":"ⲧ"}
	circum1 = {"ⲉ":"ⲉ"}
	circum2 = {"ϣⲁⲛ":"ϣⲁⲛ","ⲉ":"ⲉ",}

	pre_nom_verb = {"ϯ":"ϯ","ⲣ":"ⲣ","ϫⲓ":"ϫⲓ"}

	# Ti mutations
	noun_m = mutate("ϯ","ⲧⲓ",{k:v for k,v in noun_m.items() if "ϯ" in k},noun_m,exclude=verbs)
	noun_f = mutate("ϯ","ⲧⲓ",{k:v for k,v in noun_f.items() if "ϯ" in k},noun_f,exclude=verbs)
	verbs = mutate("ϯ","ⲧⲓ",{k:v for k,v in verbs.items() if "ϯ" in k},verbs,exclude=dict(list(noun_m.items())+list(noun_f.items())))

	norm_data = io.open(data_dir + "norm_table.tab",encoding="utf8").read().strip().replace("\r","").split("\n")
	norms = dict((line.split("\t")) for line in norm_data if "\t" in line)
	for orig, norm in norms.items():
		orig, norm = clean(orig), clean(norm)
		if orig == "ⲁ":  # from normalizing numeral alpha to oua
			continue
		if orig == "ⲉ" and norm == "ϩⲉ":  # no general rule for normalizing t-he
			continue
		if norm in forbidden:
			continue
		if norm.startswith("ϩ") and not orig.startswith("ϩ"):  # could be a theta normalization, shouldn't generalize
			continue
		if norm in noun_m and orig not in noun_m:
			noun_m[orig] = norm
		if norm in noun_f and orig not in noun_f:
			noun_f[orig] = norm
		if norm in noun_pl and orig not in noun_pl:
			noun_pl[orig] = norm
		if norm in verbs and orig not in verbs:
			verbs[orig] = norm
		if norm in adv and orig not in adv:
			adv[orig] = norm

	output = []

	clust_n_m = {k:v for k,v in noun_m.items() if clust(k)}
	clust_n_f = {k:v for k,v in noun_f.items() if clust(k)}
	labial_m_masc = {k:v for k,v in noun_m.items() if initial(k,"ⲙ")}
	labial_b_masc = {k:v for k,v in noun_m.items() if initial(k,"ⲃ")}
	labial_p_masc = {k:v for k,v in noun_m.items() if initial(k,"ⲡ") or initial(k,"ⲫ")}
	labial_b_masc.update(labial_m_masc)
	labial_b_masc.update(labial_p_masc)
	labial_noun_masc = labial_b_masc
	labial_m_fem = {k:v for k,v in noun_f.items() if initial(k,"ⲙ")}
	labial_b_fem = {k:v for k,v in noun_f.items() if initial(k,"ⲃ")}
	labial_p_fem = {k:v for k,v in noun_f.items() if initial(k,"ⲡ") or initial(k,"ⲫ")}
	labial_b_fem.update(labial_m_masc)
	labial_b_fem.update(labial_p_fem)
	labial_noun_fem = labial_b_fem

	noun_b = {k:v for k,v in dict(list(noun_m.items())+list(noun_f.items())+list(noun_pl.items())).items() if initial(k,'ⲃ')}
	noun_l = {k:v for k,v in dict(list(noun_m.items())+list(noun_f.items())+list(noun_pl.items())).items() if initial(k,'ⲗ')}
	noun_r = {k:v for k,v in dict(list(noun_m.items())+list(noun_f.items())+list(noun_pl.items())).items() if starter(k,["ⲣⲓⲣ","ⲣⲉϥ","ⲣⲙ","ⲣⲱⲙ","ⲣⲟⲙ"])}

	def o(name,indict):
		for k, v in indict.items():
			if " " in k or " " in v or k in never_normalize or "-" in k or "-" in v:
				continue
			output.append("\t".join([name,k,v]))

	del noun_m["ⲟⲩⲁϩϥ"]  # potential clash for verbal ouah=f
	del noun_not_verb["ⲟⲩⲁϩϥ"]  # potential clash for verbal ouah=f
	if "ⲃ" in verbs:
		del verbs["ⲃ"]
	if "ⲗ" in verbs:
		del verbs["ⲗ"]

	# Numbers
	digits = ["ⲟⲩⲁ","ⲟⲩⲉⲓ","ⲥⲛⲁⲩ","ⲥⲛⲧⲉ","ϣⲟⲙⲛⲧ","ϣⲟⲙⲧⲉ","ϥⲧⲟⲟⲩ","ϥⲧⲟ","ϯⲟⲩ","ϯⲉ","ⲥⲟⲟⲩ","ⲥⲟⲉ","ⲥⲁϣϥ","ⲥⲁϣϥⲉ","ϣⲙⲟⲩⲛ","ϣⲙⲟⲩⲛⲉ","ⲯⲓⲥ","ⲯⲓⲧⲉ"]
	tens = ["ⲙⲏⲧⲉ","ⲙⲏⲧ","ϫⲟⲩⲱⲧ","ϫⲟⲩⲱⲧⲉ","ⲙⲁⲁⲃ","ⲙⲁⲁⲃⲉ","ϩⲙⲉ","ⲧⲁⲉⲓⲟⲩ","ⲥⲉ","ϣϥⲉ","ϩⲙⲉⲛⲉ","ⲡⲥⲧⲁⲓⲟⲩ"]
	terminal = ["ⲟⲩⲉ","ⲟⲩⲉⲓ","ⲥⲛⲟⲟⲩⲥ","ⲥⲛⲟⲟⲩⲥⲉ","ϣⲟⲙⲧⲉ","ⲁϥⲧⲉ","ⲧⲏ","ⲁⲥⲉ","ⲥⲁϣϥⲉ","ϣⲙⲏⲛ","ϣⲙⲏⲛⲉ","ⲯⲓⲥ","ⲯⲓⲧⲉ"]
	prefix = ["ⲙⲛⲧ","ϫⲟⲩⲧ","ⲙⲁⲃ","ϩⲙⲉ","ⲧⲁⲉⲓⲟⲩ","ⲥⲉ","ϣϥⲉ","ϩⲙⲉⲛⲉ","ϩⲙⲉⲛⲉⲧ","ϩⲙⲉⲧ","ⲡⲥⲁⲧⲁⲓⲟⲩ"]
	hundred = ["ϣⲉ","ϣⲏⲧ","ϣⲙⲛⲧϣⲉ","ϥⲧⲉⲩϣⲉ"]
	thousand = ["ϣⲟ","ϣⲙⲛⲧϣⲟ"]
	large_counter = ["ϥⲧⲟⲟⲩ","ϯⲟⲩ","ϯⲉ","ⲥⲟⲟⲩ","ⲥⲁϣϥ","ϣⲙⲟⲩⲛ","ⲯⲓⲥ"]

	digits = {k:k for k in digits}
	tens = {k:k for k in tens}
	tenterminal = {k:k for k in terminal}
	tenprefix = {k:k for k in prefix}
	hundred = {k:k for k in hundred}
	thousand= {k:k for k in thousand}
	large_counter = {k:k for k in large_counter}
	digits["ϥⲧⲟⲉ"] = "ϥⲧⲟ"
	digits["ⲥϣϥ"] = "ⲥⲁϣϥ"
	digits["ⲥϣϥⲉ"] = "ⲥⲁϣϥⲉ"
	tens["ⲙⲁⲁⲙ"] = "ⲙⲁⲁⲃ"
	large_counter["ϥⲧⲟⲩ"] = "ϥⲧⲟⲟⲩ"

	# Special constructions
	pet = {"ⲡⲉⲧ":"ⲡⲉⲧ","ⲧⲉⲧ":'ⲧⲉⲧ',"ⲛⲉⲧ":"ⲛⲉⲧ","ⲡⲉϯ":"ⲡⲉⲧⲓ","ⲧⲉϯ":"ⲧⲉⲧⲓ","ⲛⲉϯ":"ⲛⲉⲧⲓ"}
	penta = {"ⲡⲉⲛⲧⲁ":"ⲡⲉⲛⲧⲁ","ⲧⲉⲛⲧⲁ":'ⲧⲉⲛⲧⲁ',"ⲛⲉⲛⲧⲁ":"ⲛⲉⲛⲧⲁ"}
	labial_pet = {"ⲡⲉⲧ":"ⲡⲉⲧ","ⲡⲉϯ":"ⲡⲉⲧⲓ"}
	labial_penta = {"ⲡⲉⲛⲧⲁ":"ⲡⲉⲛⲧⲁ"}
	mmau = {"ⲙⲙⲁⲩ":"ⲙⲙⲁⲩ","ϩⲓϩⲟⲩⲛ":"ϩⲓϩⲟⲩⲛ","ⲛϩⲟⲩⲟ":"ⲛϩⲟⲩⲟ"}  # Adverbs that go with pet-

	art_f_no_tn = {k:v for k,v in art_f.items()}

	# Serialize
	o("n",{"ⲛ":"ⲛ"})
	o("m",{"ⲙ":"ⲙ"})
	o("labial_noun_m",labial_noun_masc)
	o("labial_noun_f",labial_noun_fem)
	o("noun_b",noun_b)
	o("noun_l",noun_l)
	o("noun_r",noun_r)
	o("digits",digits)
	o("tens",tens)
	o("tenterminal",tenterminal)
	o("tenprefix",tenprefix)
	o("hundred",hundred)
	o("thousand",thousand)
	o("large_counter",large_counter)
	o("art_m_long",art_m_long)
	o("art_f_long",art_f_long)
	o("art_pl_long",art_pl_long)
	o("art_pl_r",art_pl_r)
	o("art_pl_l",art_pl_l)
	o("art_pl_b",art_pl_b)
	o("art_m",art_m)
	o("art_f",art_f)
	o("art_f_no_tn",art_f_no_tn)
	o("art_pl",art_pl)
	o("art_theta",art_theta)
	o("art_phi",art_phi)
	o("art_eth",art_eth)
	o("pet",pet)
	o("labial_pet",labial_pet)
	o("penta",penta)
	o("labial_penta",labial_penta)
	o("mmau",mmau)
	o("nf",nf)
	o("verb",verbs)
	o("stative",stative)
	o("h_verb",h_verb)
	o("noun_not_verb",noun_not_verb)
	o("conv",conv)
	o("conv_short",conv_short)
	o("et",et)
	o("je",je)
	o("na",na)
	o("ta",ta)
	o("prep",prep)
	o("prep_m",prep_m)
	o("prep_no_tn",prep_no_tn)
	o("noun_m",noun_m)
	o("noun_f",noun_f)
	o("adv",adv)
	o("name",names)
	o("circum1",circum1)
	o("circum2",circum2)
	o("clust_n_m",clust_n_m)
	o("clust_n_f",clust_n_f)
	o("h_noun_m",h_noun_m)
	o("h_noun_f",h_noun_f)
	o("noun_pl",noun_pl)
	#o("noun_pl_no_v",noun_pl_no_v)
	#o("ppos_m",ppos_m)
	#o("ppos_f",ppos_f)
	#o("ppos_pl",ppos_pl)
	o("aux_ei",aux_ei)
	o("aux_ei_no_noun",aux_ei_no_noun)
	o("v_not_n",v_not_n)
	o("pre_nom_verb",pre_nom_verb)
	o("bi_subj",bi_subj)
	o("caus",caus)
	o("inf_mark",inf_mark)
	o("tri_aux",tri_aux)
	o("tri_nom",tri_nom)
	o("tri_subj",tri_subj)
	o("ppero",ppero)

	with io.open(script_dir + "lexicon_foma.tab",'w',encoding="utf8") as f:
		f.write("\n".join(sorted(list(set(output)))))


def make_lexc():
	"""Make an XFST format .lexc file"""

	lines = io.open(script_dir+"lexicon_foma.tab",encoding="utf8").read().replace("\r","").split("\n")

	unhandled = set()
	lex = defaultdict(lambda : defaultdict())

	for line in lines:
		if "(" in line:  # Items with regex capturing groups
			unhandled.add(line)
		elif "." in line:
			continue
		else:
			cat, word, rep = line.split("\t")

			lex[cat][clean(word)] = clean(rep)

	output = []

	cont = defaultdict(set)

	cont["Root"] = set([])

	lines = io.open(script_dir+"grammar_foma.tab",encoding="utf8").read().replace("\r","").split("\n")

	for line in lines:
		if line.startswith("#") or len(line.strip())==0:
			continue
		if "+" in line:
			parts = line.split("+")
			for i in range(len(parts)-1):
				cont[parts[i]].add(parts[i+1])
			cont[parts[-1]].add("#")
			cont["Root"].add(parts[0])
		else:
			cont["Root"].add(line)

	output.append("LEXICON Root")
	output.append('')

	for starter in cont["Root"]:
		output.append(starter+" ;")

	for cat in lex:
		output.append('')
		output.append("LEXICON " + cat)
		output.append('')
		if cat in cont:
			continuation = cont[cat]
		else:
			continuation = set(["#"])

		for c in continuation:
			for word, rep in lex[cat].items():
				if " " in word or " " in rep:
					continue
				if rep != word:
					output.append(word + ":" + rep + " " + c + ";")
				else:
					output.append(word + " " + c + ";")

	with io.open(script_dir + "coptic.lexc", 'w', encoding="utf8", newline="\n") as f:
		f.write("\n".join(output) + "\n")

	with io.open(script_dir + "unhandled.txt", 'w', encoding="utf8", newline="\n") as f:
		f.write("\n".join(list(unhandled)) + "\n")


if __name__ == "__main__":
	sys.stderr.write("o Compiling lexicon_foma.tab\n")
	make_lexicon_foma()
	sys.stderr.write("o Compiling coptic.lexc\n")
	make_lexc()
	sys.stderr.write("o Building foma binary coptic_foma.bin...\n")
	try:
		proc = subprocess.Popen(["foma","-l","coptic.foma"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		(stdout, stderr) = proc.communicate()
		sys.stderr.write("o Copy coptic_foma.bin one directory up to bin/ to use new grammar\n")
	except Exception as e:
		sys.stderr.write("! Build failure!\n")
		print(e)

