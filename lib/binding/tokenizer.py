import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))
from auto_norm import normalize


def remove_chars(s, ignore):
	return "".join([c for c in s if c not in ignore])


class Token:
	def __init__(
			self,
			gold=None,
			gold_start=None,
			gold_end=None,
			gold_bound=None,
			orig=None,
			orig_start=None,
			orig_end=None
	):
		self.gold = gold
		self.orig = orig
		self.gold_start = gold_start
		self.gold_end = gold_end
		self.gold_bound = gold_bound
		self.orig_start = orig_start
		self.orig_end = orig_end

		self.normed_orig = None

	def text(self, ignore=[], use_normalized=True):
		if use_normalized and self.normed_orig:
			text = self.normed_orig
		else:
			text = self.orig
		if ignore:
			text = remove_chars(text, ignore)
		return text

	def __str__(self):
		if self.orig:
			return '<Token "%s" ("%s")>' % (self.gold, self.orig)
		return '<Token "%s">' % self.gold

	def __repr__(self):
		return '<Token gold="%s" (gold[%s:%s]) orig="%s" (orig[%s:%s])>' % (
			self.gold,
			self.gold_start,
			self.gold_end,
			self.orig,
			self.orig_start,
			self.orig_end
		)


class Tokenizer:
	"""A class that tokenizes texts, and aligns them if gold is available"""
	def __init__(
			self,
			ignore_chars=[],
			gold_token_separator="_",
			orig_token_separator=" ",
			lowercase=False,
			normalize=False,
	):
		assert type(gold_token_separator) == str
		assert type(orig_token_separator) == str
		self._gold_token_separator = gold_token_separator
		self._orig_token_separator = orig_token_separator
		self._lowercase = lowercase
		self._normalize = normalize

		self._separators = [gold_token_separator, orig_token_separator]
		self._ignore_chars = ignore_chars
		self._ignore_or_sep = ignore_chars + self._separators

	def tokenize(self, text, orig=None):
		text = text.replace("\n","")
		if self._lowercase:
			text = text.lower()
			if orig:
				orig = orig.lower()

		if orig:
			tokens = self._tokenize_gold_with_orig(text, orig)
		else:
			tokens = self._tokenize(text)

		if self._normalize:
			normalized = normalize("\n".join([token.orig for token in tokens]))
			normalized = normalized.split("\n")
			assert len(normalized) == len(tokens)
			for i, token in enumerate(tokens):
				token.normed_orig = normalized[i]

		return tokens

	def _split_gold_token(self, gold_token, g2o):
		"""Handles the case when a gold token corresponds to multiple orig tokens.
		For every occurrence of _orig_token_separator in orig, produces a new token.
		TODO: gold, gold_start, and gold_end are not modified in this process."""
		tokens = []

		big_token = gold_token
		while self._orig_token_separator in big_token.orig:
			groups = big_token.orig.split(self._orig_token_separator)

			new_orig_group = groups[0]
			remainder_orig_group = self._orig_token_separator.join(groups[1:])

			tokens.append(
				Token(
					gold=big_token.gold,
					gold_start=big_token.gold_start,
					gold_end=big_token.gold_end,
					gold_bound=True,
					orig=new_orig_group,
					orig_start=big_token.orig_start,
					orig_end=big_token.orig_start + len(new_orig_group)
				)
			)

			big_token = Token(
				gold=big_token.gold,
				gold_start=big_token.gold_start,
				gold_end=big_token.gold_end,
				gold_bound=False,
				orig=remainder_orig_group,
				# add 1 to account for the sep
				orig_start=big_token.orig_start + len(new_orig_group) + 1,
				orig_end=big_token.orig_end
			)

		tokens.append(big_token)
		return tokens

	def _tokenize_gold_with_orig(self, gold, orig):
		"""Produces a correspondence between tokens in gold and tokens in orig. Tokens
		are produced based on ORIG splits."""

		def make_alpha_index_correspondeces(gold, orig):
			"""Scan gold and orig and produce an index mapping between each alphabetical char in gold
			and the corresponding char in orig."""

			def is_not_alpha(c):
				return c in self._ignore_or_sep

			g2o = {}

			g_i = 0
			o_i = 0
			while g_i < len(gold):
				# at the beginning, we should always be on the same alphabetical char
				while g_i < len(gold) and is_not_alpha(gold[g_i]):
					g2o[g_i] = o_i
					g_i += 1
				while o_i < len(orig) and is_not_alpha(orig[o_i]):
					o_i += 1

				if g_i == len(gold):
					break

				# set up a correspondence between the two alphabetical chars
				g2o[g_i] = o_i

				# go to the next non-ignorable character in gold
				g_i += 1
				o_i += 1

			# we should have fully scanned gold
			assert g_i == len(gold)
			return g2o

		assert ([c for c in orig if c not in self._ignore_or_sep]
				== [c for c in gold if c not in self._ignore_or_sep])
		g2o = make_alpha_index_correspondeces(gold, orig)

		tokens = []
		start = 0
		for i in range(len(gold)):
			if i == len(gold) - 1 or gold[i + 1] == self._gold_token_separator:

				# add one to i for substringing later on
				gold_group = gold[start : i + 1]
				orig_group = orig[g2o[start] : g2o[i] + 1]

				# We promised that we'd deliver tokens split by orig, so we need to check to make
				# sure if the gold token contains multiple orig tokens.
				# TODO: what if orig actually overbinds? Not a problem in Marcion, might be in others
				gold_token = Token(
					gold=gold_group,
					gold_start=start,
					gold_end=i + 1,
					gold_bound=False,
					orig=orig_group,
					orig_start=g2o[start],
					orig_end=g2o[i] + 1
				)
				tokens += self._split_gold_token(gold_token, g2o)

				# assume there's only one boundary
				if i + 2 >= len(gold):
					break
				else:
					start = i + 2

		return tokens

	# a is now a list
	def _tokenize(self, orig):
		tokens = []
		start = 0
		for i in range(len(orig)):
			if i == len(orig) - 1 or orig[i + 1] == self._orig_token_separator:
				orig_tok = orig[start : i + 1]
				tokens.append(
					Token(
						orig=orig_tok,
						orig_start=start,
						orig_end=i+1
					)
				)

				# assume there's only one boundary
				if i + 2 >= len(orig):
					break
				else:
					start = i + 2

		return tokens
