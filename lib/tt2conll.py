#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
# Python port of TT2CoNLL.pl
#
# this script takes a corpus in CWB SGML format
# and converts it into the CoNLL input format using
# the POS tag column (column 2) as both the fine
# and coarse grained tag. SGML elements are deleted.
#
# Computer	NN	Computer
#
# becomes
#
# 1	Computer	Computer	NN	NN	_	_	_
#
# The script splits sentences based on a predetermined sentence
# splitting tag, at the moment defaulting to $. (STTS sentence
# punctuation)
#
# usage:
# python tt2conll.py [OPTIONS] <CORPUS>
#
# Options and arguments:
#
# -t <tagname> Use the tag <tagname> to split the corpus into sentences, default is $.
# -x <element> Use the XML element <element> to split the corpus into sentences (e.g. s)
# -h           Print this message and quit
#
# <CORPUS>     A corpus coded in CWB SGML
#
# examples:
# python tt2conll.py -t $. my_corpus.sgml > my_corpus.conll
# python tt2conll.py -t SENT my_corpus.sgml > my_corpus.conll
# python tt2conll.py -x s my_corpus.sgml > my_corpus.conll
# etc.
"""

from argparse import ArgumentParser
import io

def conllize(in_text,tag=None,element=None,no_zero=False):

	xml = False
	if element is not None:
		xml = True

	outlines = []
	counter = 1
	for line in in_text.replace("\r","").split("\n"):
		if len(line.strip()) > 0:
			tabs = line.count("\t")
			lemma = "_"
			pos = "_"
			morph = "_"
			if tabs == 0:
				tok = line
			else:
				fields = line.split("\t")
				tok = fields[0]
				pos = fields[1]
				if tabs > 1:
					lemma = fields[2]
				if tabs > 2:
					morph = fields[3]
			if not (line.startswith("<") and line.endswith(">")):  # Do not make tokens out of XML elements
				if no_zero:
					outlines.append("\t".join([str(counter), tok, lemma, pos, pos, morph, "_", "_"]))
				else:
					outlines.append("\t".join([str(counter),tok,lemma,pos,pos,morph,"0","_"]))
				counter += 1
			if xml:
				if "</" + element + ">" in line:
					counter = 1
					outlines.append("")
			else:
				if pos == tag:
					counter = 1
					outlines.append("")
	return "\n".join(outlines)


if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument("-t","--tagname",action="store",default="$.",help="Use the POS tag <tagname> to split the corpus into sentences, default is $.")
	parser.add_argument("-x","--xml_element",action="store",default=None,help="Use the XML element <element> to split the corpus into sentences (e.g. s)")
	parser.add_argument("infile",action="store",help="file to process")

	opts = parser.parse_args()

	in_data = io.open(opts.infile,encoding="utf8").read().replace("\r","")
	conllized = conllize(in_data,opts.tagname,opts.xml_element)
	print(conllized)

