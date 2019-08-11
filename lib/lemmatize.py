#!/usr/bin/python
# -*- coding: utf-8 -*-

import io
from collections import defaultdict


class Lemmatizer:

	def __init__(self, lex_file, no_unknown=True):
		self.lex = defaultdict(lambda : defaultdict(set))
		self.no_unknown = no_unknown
		self.load(lexfile=lex_file)

	def load(self,lexfile):
		lines = io.open(lexfile,encoding="utf8").read().replace("\r","").split("\n")

		for line in lines:
			if "\t" in line:
				word, pos, lemma = line.split("\t")
				self.lex[word][pos].add(lemma)

	def lemmatize(self,words_tags):
		"""words_tags: string of tab delimited word\tpos per line"""

		lines = words_tags.replace("\r","").strip().split("\n")
		spl = [line.split("\t") for line in lines if "\t" in line]
		words, tags = zip(*spl)

		output=[]
		for i, word in enumerate(words):
			pos = tags[i]
			if word in self.lex:
				if pos in self.lex[word]:
					matches = list(self.lex[word][pos])
					if len(matches) == 1:  # Unique solution
						output.append(matches[0])
						continue
					else:  # Disambiguate
						match = matches[0]
						# TODO: disambiguation code

						output.append(match)
						continue
				else:
					# word known, but not in this pos; use OOV behavior
					if self.no_unknown:
						output.append(word)
					else:
						output.append("UNKNOWN")
			else:
				if self.no_unknown:
					output.append(word)
				else:
					output.append("UNKNOWN")
		output = ["\t".join([words[i],tags[i],output[i]]) for i in range(len(words))]

		return "\n".join(output)
