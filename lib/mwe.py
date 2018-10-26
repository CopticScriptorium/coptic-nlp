#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, io, sys

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


if __name__ == "__main__":  # Test mwe
	if not PY3:
		norms = "ⲁ ⲥ ϭⲱⲗⲡ ⲉⲃⲟⲗ ⲟⲩⲧⲉ ⲣ ⲉ ⲛ ⲣⲱⲙⲉ ⲟⲩⲧⲉ ⲃⲱϣ ⲉⲃⲟⲗ".decode("utf8").split()
		lemmas = "ⲁ ⲛⲧⲟⲥ ϭⲱⲗⲡ ⲉⲃⲟⲗ ⲟⲩⲧⲉ ⲉⲓⲣⲉ ⲉ ⲡ ⲣⲱⲙⲉ ⲟⲩⲧⲉ ⲃⲱϣ ⲉⲃⲟⲗ".decode("utf8").split()
	else:
		norms = "ⲁ ⲥ ϭⲱⲗⲡ ⲉⲃⲟⲗ ⲟⲩⲧⲉ ⲣ ⲉ ⲛ ⲣⲱⲙⲉ ⲟⲩⲧⲉ ⲃⲱϣ ⲉⲃⲟⲗ".split()
		lemmas = "ⲁ ⲛⲧⲟⲥ ϭⲱⲗⲡ ⲉⲃⲟⲗ ⲟⲩⲧⲉ ⲉⲓⲣⲉ ⲉ ⲡ ⲣⲱⲙⲉ ⲟⲩⲧⲉ ⲃⲱϣ ⲉⲃⲟⲗ".split()
	res = tag_mwes(norms,lemmas)
	print(res)
