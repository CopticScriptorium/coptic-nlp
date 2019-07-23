#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
norm - Python
V3.0.0
Extended python port of the Perl script normalizing Sahidic Coptic text to standard spelling.
New in V3: fall back to finite state normalizer for OOV items and other enhancements.

Usage:  norm.py [options] <FILE>

Options and argument:

-h              print this [h]elp message and quit
-s              use [s]ahidica Bible specific normalization rules
-t              use [t]able containing previous normalizations (first column is diplomatic text, last column is normalized)
-m              [m]ethod for finitestate fallback, one of 'foma', 're' or 'none'

<FILE>    A text file encoded in UTF-8 without BOM


Examples:

Normalize a Coptic plain text file in UTF-8 encoding (without BOM):
python norm.py in_Coptic_utf8.txt > out_Coptic_normalized.txt
python norm.py -t norm_table.tab in_Coptic_utf8.txt > out_Coptic_normalized.txt

Copyright 2013-2019, Amir Zeldes & Caroline T. Schroeder

This program is free software.
"""

from argparse import ArgumentParser
import io, sys, os, re
from collections import defaultdict

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
data_dir = script_dir + ".." + os.sep + "data" + os.sep


orig_chars = set(["̈", "", "̄", "̀", "̣", "`", "̅", "̈", "̂", "︤", "︥", "︦", "⳿", "~", "\n", "̇", " ", "‴", "#", "᷍", "⸍", "›", "‹"])


#@profile
def normalize(in_data,table_file=None,sahidica=False,method="foma",no_unknown=True):
	def clean(text):
		if "(" not in text and ")" not in text:  # Retain square brackets if item has capturing groups
			if len(text) > 1:
				text = text.replace("[","").replace("]","")
		return ''.join([c for c in text if c not in orig_chars]).lower()

	outlines=[]
	if table_file is None:
		# Use default location for norm table
		table_file = data_dir + os.sep + "norm_table.tab"
	try:
		norm_lines = io.open(table_file,encoding="utf").read().replace("\r","").split("\n")
	except Exception as e:
		sys.stderr.write("could not find normalization table file at " + table_file + "\n")
		sys.exit(0)

	norms = defaultdict(lambda : defaultdict(int))
	for line in norm_lines:
		if "\t" in line:
			fields = line.split("\t")
			norms[clean(fields[0])][clean(fields[1])]+=1
	temp = {}
	for orig in norms:
		max_norm = max(norms[orig],key=lambda x: norms[orig][x])
		temp[orig] = max_norm
	norms = temp
	norms["ⲉⲣ"] = "ⲉⲣ"  # Prevent incorrect generalization from training data

	lines = [clean(line) for line in in_data.strip().split("\n")]
	unk_lines = list(set([line for line in lines if line not in norms]))

	use_foma = True if method.lower()=="foma" else False
	if method!="none" and len(unk_lines)>0:
		if use_foma:
			from foma_norm import FomaNorm
			fs = FomaNorm(no_unknown=no_unknown)
			fm_norms = fs.normalize(unk_lines)
			for i, norm in enumerate(fm_norms):
				if unk_lines[i] != norm:
					norms[unk_lines[i]] = norm
		else:
			from fs_norm import FSNorm
			# Get set of char n-grams attested in data
			gram = 5
			char_n_grams = [in_data[i:i+gram].lower() for i in range(len("\n".join(unk_lines))-gram)]
			char_n_grams = set([g for g in char_n_grams if "\n" not in g])

			# Build normalizer, ignoring items that can't possibly match the data to increase performance speed
			fs = FSNorm(grams=char_n_grams)


	for line in lines:
		if line in norms:
			line = norms[line]
		else:
			line = line.replace("|","").replace("[","").replace("]","")
			line = line.replace("⳯","ⲛ")
			line = line.replace("[`̂︦︥̄⳿̣̣̇̈̇̄̈︤᷍]","")
			line = line.replace("̂","")
			line = line.replace("`","")
			line = line.replace("᷍","")
			line = line.replace("̣","")
			line = re.sub(r'([ⲁⲃⲅⲇⲉⲍⲏⲑⲓⲕⲗⲙⲛⲥⲟⲡⲝⲣⲧⲩⲱⲯϭϣϩϥϯ])[·.]([ⲁⲃⲅⲇⲉⲍⲏⲑⲓⲕⲗⲙⲛⲥⲟⲡⲝⲣⲧⲩⲱⲯϭϣϩϥϯ])',r'\1\2',line)  # remove punctuation inside alphabetic word

			clean = line
			if line in norms:
				line = norms[line]
			elif method=="re":
				line = fs.normalize(line)

			# Known regex substitutions
			line = re.sub(r"(^|_)ⲓⲏⲗ($|_)", r"\1ⲓⲥⲣⲁⲏⲗ\2", line)
			line = re.sub(r"(^|_)ⲓⲏ?ⲥ($|_)", r"\1ⲓⲏⲥⲟⲩⲥ\2", line)
			line = re.sub(r"(^|_)ϫⲟⲓⲥ($|_)", r"\1ϫⲟⲉⲓⲥ\2", line)
			line = re.sub(r"ⲭⲣ?ⲥ($|_)", r"ⲭⲣⲓⲥⲧⲟⲥ\1", line)
			line = re.sub(r"ⲡⲛⲓⲕⲟ([ⲛⲥ]($|_))", r"ⲡⲛⲉⲩⲙⲁⲧⲓⲕⲟ\1", line)
			line = re.sub(r"(^|_)ϯⲟⲩⲇⲁⲓⲁ($|_)", r"\1ⲧⲓⲟⲩⲇⲁⲓⲁ\2", line)
			line = re.sub(r"(^|_)ⲡⲛⲁ($|_)", r"\1ⲡⲛⲉⲩⲙⲁ\2", line)
			line = re.sub(r"(^|_)ⲃⲁⲍⲁⲛⲓⲍⲉ($|_)", r"\1ⲃⲁⲥⲁⲛⲓⲍⲉ\2", line)
			line = re.sub(r"(^|_)ⲃⲁⲍⲁⲛⲟⲥ($|_)", r"\1ⲃⲁⲥⲁⲛⲟⲥ\2", line)
			line = re.sub(r"(^|_)ϩⲓⲗⲏⲙ($|_)", r"\1ϩⲓⲉⲣⲟⲩⲥⲁⲗⲏⲙ\2", line)
			line = re.sub(r"(^|_)ⲥ[ⳁⲣ]ⲟⲥ($|_)", r"\1ⲥⲧⲁⲩⲣⲟⲥ\2", line)
			line = re.sub(r"(^|_)ⲕⲗⲏⲣⲟⲛⲟⲙⲓ($|_)", r"\1ⲕⲗⲏⲣⲟⲛⲟⲙⲉⲓ\2", line)
			line = re.sub(r"(^|_)ⲓⲱⲧ($|_)", r"\1ⲉⲓⲱⲧ\2", line)
			line = re.sub(r"(^|_)ⲓⲟⲧⲉ($|_)", r"\1ⲉⲓⲟⲧⲉ\2", line)
			line = re.sub(r"(^|_)ϩⲣⲁⲉⲓ($|_)", r"\1ϩⲣⲁⲓ\2", line)
			line = re.sub(r"(^|_)ⲡⲏⲟⲩⲉ($|_)", r"\1ⲡⲏⲩⲉ\2", line)
			line = re.sub(r"(^|_)ϩⲃⲏⲟⲩⲉ($|_)", r"\1ϩⲃⲏⲩⲉ\2", line)
			line = re.sub(r"(^|_)ⲓⲉⲣⲟⲥⲟⲗⲩⲙⲁ($|_)", r"\1ϩⲓⲉⲣⲟⲩⲥⲁⲗⲏⲙ\2", line)
			line = re.sub(r"ⲑⲓⲗⲏⲙ($|_)", r"ⲧϩⲓⲉⲣⲟⲩⲥⲁⲗⲏⲙ\1", line)
			line = re.sub(r"ⲙⲟⲛⲟⲭⲟⲥ($|_)", r"ⲙⲟⲛⲁⲭⲟⲥ\1", line)
			line = re.sub(r"(^|_)ⲡⲓⲑⲉ($|_)", r"\1ⲡⲉⲓⲑⲉ\2", line)
			line = re.sub(r"(^|_)ⲡⲣⲟⲥⲕⲁⲣⲧⲉⲣⲓ($|_)", r"\1ⲡⲣⲟⲥⲕⲁⲣⲧⲉⲣⲓⲁ\2", line)
			line = re.sub(r"(^|[_ ]|ϫⲉ)ⲙⲡⲁⲧⲉ([ⲕϥⲥⲛ][^_ ]*)($|_)", r"\1ⲙⲡⲁⲧ\2\3", line)
			line = re.sub(r"(^|[_ ]|ϫⲉ)ⲙⲡⲁϯ([^_ ]+)($|_)", r"\1ⲙⲡⲁⲧⲓ\2\3", line)
			line = re.sub(r'ⲉⲑⲟⲟⲩ($|_)',r'ⲉⲧϩⲟⲟⲩ\1',line)

			# Sahidica specific replacements
			if sahidica:
				line = re.sub(r'ⲟⲉⲓ($|_| )',"ⲉⲓ",line)
				line = re.sub(r'^([ⲡⲧⲛ])ⲉⲉⲓ)',r"\1ⲉⲓ",line)

			norms[clean] = line

		outlines.append(line)
	return "\n".join(outlines)


if __name__=="__main__":

	parser = ArgumentParser()
	parser.add_argument("-s","--sahidica",action="store_true",help="use [s]ahidica Bible specific normalization rules")
	parser.add_argument("-t","--table",action="store",default=None,help="use [t]able containing previous normalizations (first column is diplomatic text, last column is normalized)")
	parser.add_argument("-m","--method",action="store",choices=["foma","re","none"],default="foma",help="which finite state fallback method to use")
	parser.add_argument("infile",action="store",help="file to process")

	opts = parser.parse_args()

	in_data = io.open(opts.infile,encoding="utf8").read().replace("\r","")
	normalized = normalize(in_data,table_file=opts.table,sahidica=opts.sahidica,method=opts.method)
	print(normalized)

