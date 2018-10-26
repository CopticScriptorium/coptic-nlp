#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
lang.py - Python implementation of Scriptorium _enrich.pl for language of origin lookup V1.0

This script enriches lines based on the first tab-delimited column of that line with values from a lexicon file
in a new column of the output file.

Usage:  python lang.py [-n] -l <LEXICON> <IN_FILE>

Options and arguments:

-h              print this [h]elp message and quit
-l              [l]exicon file (required)
-n              [n]o built-in patterns (only use lexicon)

<IN_FILE>    A text file one category per line, only text up to the first tab is used for lexicon lookup

"""

from argparse import ArgumentParser
import io, os, sys, re


def lookup_lang(in_data,lexicon=None,words=False):

	outlines=[]
	if lexicon is None:
		# Use default location for norm table
		lexicon = ".." + os.sep + "data" + os.sep + "lang_lexicon.tab"
	try:
		lang_data = io.open(lexicon,encoding="utf8").read().replace("\r","").split("\n")
	except IOError as e:
		sys.stderr.write("could not find lexicon file at " + lexicon + "\n")
		sys.exit(0)
	lang_dict = {}
	min_pref = 100
	max_pref = 0
	min_suf = 100
	max_suf = 0
	for line in lang_data:
		if "\t" in line:
			word, lang = line.split("\t")[:2]
			lang_dict[word] = lang
			if word.endswith("*"):
				max_pref = len(word) - 1 if len(word) - 1 > max_pref else max_pref
				min_pref = len(word) - 1 if len(word) - 1 < min_pref else min_pref
			elif word.startswith("*"):
				max_suf = len(word) - 1 if len(word) - 1 > max_suf else max_suf
				min_suf = len(word) - 1 if len(word) - 1 < min_suf else min_suf
	if min_suf > max_suf:
		min_suf = max_suf
	if min_pref > max_pref:
		min_pref = max_pref

	for line in in_data.strip().split("\n"):
		line = re.sub(r'^([^\s]+).*',r'\1',line)  # Keep only first column
		l = ""
		if line in lang_dict:
			l = lang_dict[line]
		else:
			for i in range(min_pref,max_pref+1):
				substr = line[:i] + "*"
				if substr in lang_dict:
					l = lang_dict[substr]
					break
			if l == "":
				for i in range(min_suf, max_suf + 1):
					substr = "*" + line[i:]
					if substr in lang_dict:
						l = lang_dict[substr]
						break
		if not words:
			outlines.append(l)
		else:
			outlines.append("".join([line,"\t",l]))
	return "\n".join(outlines)


if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument("-l","--lexicon",action="store",default="lexicon.txt",help="File for language lookup")
	parser.add_argument("-w","--words",action="store_true",help="Output the words too, not just languages")
	parser.add_argument("infile",action="store",help="file to process")

	opts = parser.parse_args()

	in_data = io.open(opts.infile,encoding="utf8").read().replace("\r","")
	langed = lookup_lang(in_data,lexicon=opts.lexicon,words=opts.words)
	print(langed)

