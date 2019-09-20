#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, io, sys, re

"""
This script goes over a running list of paired norm words and lemmas to find multiword expressions based on a list
of candidate expressions from a lexicon. Overlapping spans are prohibited and spans are detected up to a maximum
length (default=4).
"""

script_dir = os.path.dirname(os.path.realpath(__file__))
PY3 = sys.version_info[0] == 3


def tag_mwes(norms, lemmas, max_length=4):
	lex = io.open(script_dir + os.sep + ".." + os.sep + "data" + os.sep + "mwe.tab",encoding="utf8").read().replace("\r","").strip().split("\n")
	lex = set(lex)

	results = []
	i = 0
	while i < len(norms)-1:
		max_len = max_length if i + max_length < len(norms) - 1 else len(norms)-i
		for j in range(2,max_len+1):
			norm_candidate = " ".join(norms[i:i+j])
			lemma_candidate = " ".join(lemmas[i:i+j])
			if not PY3:
				norm_candidate = unicode(norm_candidate)
				lemma_candidate = unicode(lemma_candidate)
			if norm_candidate in lex:
				results.append((i,i+j-1,norm_candidate))
				i += j-1
				break
			elif lemma_candidate in lex:
				results.append((i,i+j-1,lemma_candidate))
				i += j-1
				break
		i += 1

	#with io.open("/var/www/html/coptic-nlp/debug.txt",'w', encoding="utf8") as f:
	#	f.write(str(results))
	return results


def read_attributes(input,attribute_name):
	out_stream =""
	for line in input.split('\n'):
		if attribute_name + '="' in line:
			m = re.search(attribute_name+r'="([^"]*)"',line)
			if m is None:
				print("ERR: cant find " + attribute_name + " in line: " + line)
				attribute_value = ""
			else:
				attribute_value = m.group(1)
			if len(attribute_value)==0:
				attribute_value = "_warn:empty_"+attribute_name+"_"
			out_stream += attribute_value +"\n"
	return out_stream


def add_mwe_to_sgml(sgml):
	norms = read_attributes(sgml,"norm")
	lemmas = read_attributes(sgml,"norm")
	mwe_positions = tag_mwes(norms.split("\n"),lemmas.split("\n"))
	output = inject_tags(sgml, mwe_positions)
	return output


def inject_tags(in_sgml,insertion_specs,around_tag="norm",inserted_tag="multiword"):
	"""

	:param in_sgml: input SGML stream including tags to surround with new tags
	:param insertion_specs: list of triples (start, end, value)
	:param around_tag: tag of span to surround by insertion
	:return: modified SGML stream
	"""
	if len(insertion_specs) == 0:
		return in_sgml

	counter = -1
	next_insert = insertion_specs[0]
	insertion_counter = 0
	outlines = []
	for line in in_sgml.split("\n"):
		if line.startswith("<" + around_tag + " "):
			counter += 1
			if next_insert[0] == counter:  # beginning of a span
				outlines.append("<" + inserted_tag + " " + inserted_tag + '="' + next_insert[2] + '">')
		outlines.append(line)
		if line.startswith("</" + around_tag + ">"):
			if next_insert[1] == counter:  # end of a span
				outlines.append("</" + inserted_tag + ">")
				insertion_counter += 1
				if len(insertion_specs) > insertion_counter:
					next_insert = insertion_specs[insertion_counter]

	return "\n".join(outlines)


if __name__ == "__main__":  # Test mwe
	if not PY3:
		norms = "ⲁ ⲥ ϭⲱⲗⲡ ⲉⲃⲟⲗ ⲟⲩⲧⲉ ⲣ ⲉ ⲛ ⲣⲱⲙⲉ ⲟⲩⲧⲉ ⲃⲱϣ ⲉⲃⲟⲗ".decode("utf8").split()
		lemmas = "ⲁ ⲛⲧⲟⲥ ϭⲱⲗⲡ ⲉⲃⲟⲗ ⲟⲩⲧⲉ ⲉⲓⲣⲉ ⲉ ⲡ ⲣⲱⲙⲉ ⲟⲩⲧⲉ ⲃⲱϣ ⲉⲃⲟⲗ".decode("utf8").split()
	else:
		norms = "ⲁ ⲥ ϭⲱⲗⲡ ⲉⲃⲟⲗ ⲟⲩⲧⲉ ⲣ ⲉ ⲛ ⲣⲱⲙⲉ ⲟⲩⲧⲉ ⲃⲱϣ ⲉⲃⲟⲗ".split()
		lemmas = "ⲁ ⲛⲧⲟⲥ ϭⲱⲗⲡ ⲉⲃⲟⲗ ⲟⲩⲧⲉ ⲉⲓⲣⲉ ⲉ ⲡ ⲣⲱⲙⲉ ⲟⲩⲧⲉ ⲃⲱϣ ⲉⲃⲟⲗ".split()
	res = tag_mwes(norms,lemmas)
	print(res)
