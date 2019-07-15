import os
import io
import types

from .const import UNKNOWN_CHAR

import numpy as np
from sklearn.preprocessing import OneHotEncoder

UNKNOWN_POS = "UNKNOWN"


def read_binding_freq_file(path):
	class BindingFreq:
		def __init__(self, group, n_bound, n_not_bound, p_bound):
			self.group = group
			self.n_bound = int(n_bound)
			self.n_not_bound = int(n_not_bound)
			self.p_bound = float(p_bound)

		def __str__(self):
			return self.__repr__()

		def __repr__(self):
			return '<BindingFreq group="%s" p_bound="%s" n_bound="%s" n_not_bound="%s">' % (
				self.group,
				self.p_bound,
				self.n_bound,
				self.n_not_bound
			)

	if not os.path.isfile(path):
		raise Exception("Could not find a binding frequency file at '" + path + "'.")

	detoks = io.open(path, encoding="utf8").read().replace("\r", "").strip().split("\n")

	table = {}
	for line in detoks:
		if line.startswith("#"):
			continue
		# ignore "aggressive" entries for now
		if line.startswith("%"):
			continue

		line = line.split("\t")
		assert len(line) == 4, "Malformed line in " + path
		table[line[0]] = BindingFreq(*line)

	return table


def read_pos_file(path):
	if not os.path.isfile(path):
		raise Exception("Could not find a binding frequency file at '" + path + "'.")

	file = io.open(path, encoding="utf8").read().replace("\r", "").strip().split("\n")

	table = {}
	for line in file:
		if line.startswith("#"):
			continue

		line = line.split("\t")
		assert len(line) == 3, "Malformed line in " + path
		table[line[0]] = line[1]

	return table


def windowed_feature(out_of_window_value=None):
	"""A decorator to simplify writing windowed features. Given a function that is given the arguments
	self, token, and i and returns either a feature or a list of features, it iterates that function
	over a token window dictated by the parameters self._n_groups_right and self._n_groups_left. Also
	returns self to maintain the Featurizer's fluent API.

	If the out of window value is callable, it is called on self."""

	# inner_decorator is needed so we can give windowed_feature parameters
	# see http://scottlobdell.me/2015/04/decorators-arguments-python/
	def inner_decorator(func):

		def wrapper(self, *args, **kwargs):
			feat_cache = {}
			for i in range(len(self._tokens)):
				for j in range(i - self._n_groups_left, i + self._n_groups_right + 1):
					# build the feature
					if j not in range(len(self._tokens)):
						if callable(out_of_window_value):
							feature = out_of_window_value(self)
						else:
							feature = out_of_window_value
					elif j in feat_cache:
						feature = feat_cache[j]
					else:
						token = self._tokens[j]
						feature = func(self, token, j, *args, **kwargs)
						feat_cache[j] = feature

					# add it
					if type(feature) == list:
						self._feats[i] += feature
					else:
						self._feats[i] += [feature]
			return self

		return wrapper
	return inner_decorator


class Featurizer:
	"""Produces token-level featurizations."""
	def __init__(
			self,
			ignore_chars=[],
			n_groups_left=1,
			n_groups_right=2,
			orig_token_separator=" ",
			binding_freq_file_path=None,
			pos_file_path=None,
	):
		self._ignore_chars = ignore_chars
		self._n_groups_left = n_groups_left
		self._n_groups_right = n_groups_right
		self._orig_token_separator = orig_token_separator

		self._binding_freq_table = read_binding_freq_file(binding_freq_file_path)

		# pos encoding
		pos_table = read_pos_file(pos_file_path)
		self._pos_table = pos_table
		self._pos_encoder = OneHotEncoder(handle_unknown='ignore')
		self._pos_encoder.fit(np.array(list(pos_table.values()) + [UNKNOWN_POS]).reshape(-1, 1))
		# convenience function for encoding single values--monkey patch it onto the instance
		def transform_single(self, x):
			return self.transform(np.array(x).reshape(-1, 1)).todense().tolist()[0]
		self._pos_encoder.transform_single = types.MethodType(transform_single, self._pos_encoder)

		self._char_encoder = None

		self._tokens = []
		self._feats = []

	def _init_char_encoder(self, tokens):
		vocab = list(set("".join([t.orig for t in tokens])))
		self._char_encoder = OneHotEncoder(handle_unknown='ignore')
		self._char_encoder.fit(np.array(vocab + [UNKNOWN_CHAR]).reshape(-1, 1))
		# convenience function for encoding single values--monkey patch it onto the instance
		def transform_single(self, x):
			return self.transform(np.array(x).reshape(-1, 1)).todense().tolist()[0]
		self._char_encoder.transform_single = types.MethodType(transform_single, self._char_encoder)

	def load_tokens(self, tokens):
		self._tokens = tokens
		self._init_char_encoder(tokens)

		# initialize a feature list for each token
		self._feats = []
		for i in range(len(tokens)):
			self._feats.append([])

		return self

	def features(self):
		return self._feats

	def labels(self):
		return [1 if t.gold_bound else 0 for t in self._tokens]

	@windowed_feature(out_of_window_value=0)
	def add_bound_count(self, token, i):
		orig = token.text(ignore=self._ignore_chars)
		if orig in self._binding_freq_table:
			return self._binding_freq_table[orig].n_bound
		else:
			return 0

	@windowed_feature(out_of_window_value=0)
	def add_not_bound_count(self, token, i):
		orig = token.text(ignore=self._ignore_chars)
		if orig in self._binding_freq_table:
			return self._binding_freq_table[orig].n_not_bound
		else:
			return 0

	@windowed_feature(out_of_window_value=0.5) # TODO: should this be 0.5?
	def add_prob_bound(self, token, i):
		orig = token.text(ignore=self._ignore_chars)
		if orig in self._binding_freq_table:
			return self._binding_freq_table[orig].p_bound
		else:
			return 0.5 # TODO: see above

	@windowed_feature(out_of_window_value=0)
	def add_length(self, token, i):
		return len(token.text(ignore=self._ignore_chars))

	@windowed_feature(out_of_window_value=lambda self: self._pos_encoder.transform_single(UNKNOWN_POS))
	def add_pos(self, token, i):
		orig = token.text(ignore=self._ignore_chars)
		pos = self._pos_table[orig] if orig in self._pos_table else UNKNOWN_POS
		feature = self._pos_encoder.transform_single(pos)
		return feature

	@windowed_feature(out_of_window_value=lambda self: self._char_encoder.transform_single(UNKNOWN_CHAR))
	def add_first_letter(self, token, i):
		orig = token.text(ignore=self._ignore_chars)
		return self._char_encoder.transform_single(orig[0])

	@windowed_feature(out_of_window_value=lambda self: self._char_encoder.transform_single(UNKNOWN_CHAR))
	def add_last_letter(self, token, i):
		orig = token.text(ignore=self._ignore_chars)
		return self._char_encoder.transform_single(orig[-1])
