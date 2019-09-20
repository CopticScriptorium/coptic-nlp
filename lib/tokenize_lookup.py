#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, io, sys

PY3 = sys.version_info[0] > 2

orig_chars = set(["̈", "", "̄", "̀", "̣", "`", "̅", "̈", "̂", "︤", "︥", "︦", "⳿", "~", "\n", "̇", " ", "‴", "#", "᷍", "⸍", "›", "‹","[","]"])


def clean(text):
	if len(text) < 2:
		return text
	else:
		orig = text
		text = ''.join([c for c in text if c not in orig_chars])
		if len(text) < 1:
			text = orig
		return text


def lookup_tokenize(norms,underscore_oov=False,seg_table=None):
	if seg_table is None:
		seg_table = os.path.dirname(os.path.realpath(__file__)) + os.sep +".." + os.sep + "data" +os.sep+"segmentation_table.tab"

	rows = io.open(seg_table,encoding="utf8").read().replace("\r","").strip().split("\n")
	tuples = [row.split("\t") for row in rows if "\t" in row]
	segs = dict((clean(t[0]),clean(t[1])) for t in tuples)
	norms = [clean(norm) for norm in norms]

	tokenized = []

	for norm in norms:
		if norm in segs:
			tokenized.append(segs[norm])
		else:
			if underscore_oov:
				tokenized.append("_")
			else:
				tokenized.append(norm)

	return tokenized


if __name__ == "__main__":
	from argparse import ArgumentParser
	p = ArgumentParser()
	p.add_argument("infile")
	p.add_argument("-o","--oov_underscore",action="store_true",help="output underscore for OOV items")
	opts = p.parse_args()

	norms = io.open(opts.infile,encoding="utf8").read().replace("\r","").split("\n")
	tokenized = lookup_tokenize(norms,underscore_oov=opts.oov_underscore)
	tokenized = "\n".join(tokenized) + "\n"
	if PY3:
		sys.stdout.buffer.write(tokenized.encode("utf8"))
	else:
		sys.stdout.write(tokenized.encode("utf8"))
