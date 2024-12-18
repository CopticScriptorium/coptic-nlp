#!/usr/bin/python
# -*- coding: utf-8 -*-

import io
import os.path
import sys
from collections import defaultdict

# Words after which the lemma of ⲧⲉⲛ should be ⲛⲑⲱⲧⲉⲛ in Bohairic
boh_ten2 = set(["ⲉⲣⲉ", "ⲁⲣⲉ", "ⲉⲧⲁⲣⲉ", "ⲛⲁⲣⲉ", "ⲙⲡⲉ", "ⲙⲡⲁⲧⲉ", "ϣⲁⲧⲉ", "ϣⲁⲣⲉ", "ⲛⲧⲉ"])

class Lemmatizer:

	def __init__(self, lex_file, no_unknown=True, dialect="sahidic"):
		self.lex = defaultdict(lambda : defaultdict(set))
		self.no_unknown = no_unknown
		self.dialect = dialect
		self.load(lexfile=lex_file)

	def load(self,lexfile):
		lines = io.open(lexfile,encoding="utf8").read().replace("\r","").split("\n")

		for l, line in enumerate(lines):
			if "\t" in line:
				try:
					word, pos, lemma = line.split("\t")
				except ValueError:
					sys.stderr.write("Error in lexicon on line " + str(l+1) + " of " + os.path.basename(lexfile) + "\n")
					sys.stderr.write(line + "\n")
					quit()
				self.lex[word][pos].add(lemma)

	def lemmatize(self,words_tags, bg_positions=None):
		"""words_tags: string of tab delimited word\tpos per line"""

		lines = words_tags.replace("\r","").strip().split("\n")
		spl = [line.split("\t") for line in lines if "\t" in line]
		words, tags = zip(*spl)

		output=[]
		for i, word in enumerate(words):
			position = bg_positions[i] if bg_positions else None
			prev_word = words[i-1] if i > 0 else "_"
			next_word = words[i+1] if i < len(words)-1 else "_"
			pos = tags[i]
			next_pos = tags[i+1] if i < len(words)-1 else "_"
			prev_pos = tags[i-1] if i > 0 else "_"

			if word in self.lex:
				if pos in self.lex[word]:
					matches = sorted(list(self.lex[word][pos]))
					if len(matches) == 1:  # Unique solution
						output.append(matches[0])
						continue
					else:  # Disambiguate
						match = matches[0]
						# TODO: disambiguation code
						if self.dialect == "bohairic":
							if word == "ⲧⲉⲛ":
								if prev_word in boh_ten2:
									match = "ⲛⲑⲱⲧⲉⲛ"
								else:
									match = "ⲁⲛⲟⲛ"
							elif pos in ["PPOS","PDEM"]:
								if match in ["ⲡⲁ","ⲫⲁ"]:
									if next_pos in ["ART","PDEM","PPOS"]:
										match = "ⲫⲁ"
									else:
										match = "ⲡⲁ"
								elif match in ["ⲡⲁⲓ","ⲫⲁⲓ"]:
									if next_pos in ["N"]:
										match = "ⲡⲁⲓ"
									else:
										match = "ⲫⲁⲓ"

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
					lemma = word
					if pos == "VIMP":
						if word.startswith("ⲁⲣⲓ"):
							if self.dialect == "sahidic":
								lemma = "ⲣ" + word[3:]
							elif self.dialect == "bohairic":
								lemma = "ⲉⲣ" + word[3:]
					output.append(lemma)
				else:
					output.append("UNKNOWN")
		output = ["\t".join([words[i],tags[i],output[i]]) for i in range(len(words))]

		return "\n".join(output)
