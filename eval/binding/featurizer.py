import sys
import os
import io
import types
import numpy as np
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
import unicodedata as uni

from .const import UNKNOWN_CHAR
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))
from auto_norm import normalize

UNKNOWN_POS = "UNKNOWN"


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


def read_binding_freq_file(path):

	if not os.path.isfile(path):
		raise Exception("Could not find a binding frequency file at '" + path + "'.")

	detoks = io.open(path, encoding="utf8").read().replace("\r", "").strip().split("\n")

	table = {}
	for line in detoks:
		if line.startswith("#"):
			continue

		# include "aggressive" entries for now
		if line.startswith("%"):
			line = line[1:]

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
		if line[0] in table:
			table[line[0]] += "|" + line[1]
		else:
			table[line[0]] = line[1]

	return table


def read_group_freq_file(path, ignore):
	if not os.path.isfile(path):
		raise Exception("Could not find a binding frequency file at '" + path + "'.")

	file = io.open(path, encoding="utf8").read().replace("\r", "").strip().split("\n")

	table = {}
	for line in file:
		if line.startswith("#"):
			continue

		line = line.split("\t")
		assert len(line) == 2, "Malformed line in " + path
		group, freq = line

		group = line[0]
		group = "".join([c for c in group if c not in ignore])
		if group in table:
			table[group] = int(freq) + int(table[group])
		else:
			table[group] = int(freq)

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
			n_groups_left = (
				kwargs.pop("n_groups_left") if "n_groups_left" in kwargs
				else kwargs.pop("left") if "left" in kwargs
				else self._n_groups_left
			)
			n_groups_right = (
				kwargs.pop("n_groups_right") if "n_groups_right" in kwargs
				else kwargs.pop("right") if "right" in kwargs
				else self._n_groups_right
			)
			skip_self = kwargs.pop("skip_self") if "skip_self" in kwargs else None

			# TODO: this only works for label encoded features
			i=0
			for j in range(i - n_groups_left, i + n_groups_right + 1):
				if j == i and skip_self:
					continue
				featname = func.__name__[4:] + ("+" if j-i >=0 else "") + str(j - i)
				if featname not in self.feature_names:
					if func.__name__ in ["add_right_substr_pos", "add_left_substr_pos"]:
						self.feature_names.append(featname + " (pos)")
						self.feature_names.append(featname + " (proportion)")
					else:
						self.feature_names.append(featname)

			for i in range(len(self._tokens)):
				for j in range(i - n_groups_left, i + n_groups_right + 1):
					if j == i and skip_self:
						continue
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


# convenience function for encoding single values--monkey patch it onto an instance of an encoder
def transform_single(self, x):
	a = self.transform(np.array(x).reshape(-1, 1))
	if type(a) != np.ndarray:
		a = a.todense()[0]
	a = a.tolist()
	if type(a[0]) == list:
		a = a[0]
	return a


class Featurizer:
	encoder_map = {
		'one_hot': OneHotEncoder,
		'label': LabelEncoder
	}

	"""Produces token-level featurizations."""
	def __init__(
		self,
		n_groups_left,
		n_groups_right,
		ignore_chars=[],
		orig_token_separator=" ",
		binding_freq_file_path=None,
		pos_file_path=None,
		group_freq_file_path=None,
		encoder='one_hot',
	):
		assert encoder in Featurizer.encoder_map, "Encoder must be one of 'one_hot', 'label'."
		# assume that we have a linear model iff encoding is one-hot
		self._linear = encoder == 'one_hot'

		self._ignore_chars = ignore_chars
		self._n_groups_left = n_groups_left
		self._n_groups_right = n_groups_right
		self._orig_token_separator = orig_token_separator

		if binding_freq_file_path:
			self._binding_freq_table = read_binding_freq_file(binding_freq_file_path)

		# pos encoding
		if pos_file_path:
			pos_table = read_pos_file(pos_file_path)
			self._pos_table = pos_table
			self._pos_encoder = Featurizer.encoder_map[encoder]()
			self._pos_vocab = list(pos_table.values()) + [UNKNOWN_POS]
			self._pos_encoder.fit(np.array(self._pos_vocab).reshape(-1, 1))
			self._pos_encoder.transform_single = types.MethodType(transform_single, self._pos_encoder)

		if group_freq_file_path:
			self._group_freq_table = read_group_freq_file(group_freq_file_path, ignore_chars)

		# char encoding
		self._char_vocab = []
		self._char_encoder = Featurizer.encoder_map[encoder]()

		self._tokens = []
		self._feats = []
		self.feature_names = []

		self._normalizer_responses = {}

	def _undefined_count(self):
		return 0 if self._linear else -1

	def _undefined_prob(self):
		return 0.5 if self._linear else -1

	def _init_char_encoder(self, tokens):
		self._char_vocab = list(set("".join([t.orig for t in tokens]))) + [UNKNOWN_CHAR]
		self._char_encoder.fit(np.array(self._char_vocab).reshape(-1, 1))
		self._char_encoder.transform_single = types.MethodType(transform_single, self._char_encoder)

	def load_tokens(self, tokens, training=False):
		self._tokens = tokens
		if training:
			self._init_char_encoder(tokens)

		# initialize a feature list for each token
		self._feats = []
		for i in range(len(tokens)):
			self._feats.append([])

		lines = []
		for i in range(len(tokens)):
			if i + 1 == len(tokens):
				continue
			combined_origs = tokens[i].orig + tokens[i + 1].orig
			lines.append(combined_origs)
		resps = normalize("\n".join(lines), no_unknown=False)
		for i in range(len(resps.split("\n"))):
			self._normalizer_responses[i] = resps[i]

		return self

	def features(self):
		return self._feats

	def labels(self):
		return [1 if t.gold_bound else 0 for t in self._tokens]

	@windowed_feature(out_of_window_value=lambda self: self._undefined_count())
	def add_group_count(self, token, i):
		orig = token.text(ignore=self._ignore_chars)
		if orig in self._group_freq_table:
			return self._group_freq_table[orig]
		else:
			return self._undefined_count()

	@windowed_feature(out_of_window_value=lambda self: self._undefined_count())
	def add_combined_token_group_count(self, token, i):
		if i + 1 == len(self._tokens):
			return 0
		next_token = self._tokens[i + 1]
		combined_text = token.text(ignore=self._ignore_chars) + next_token.text(ignore=self._ignore_chars)
		if combined_text in self._group_freq_table:
			return self._group_freq_table[combined_text]
		else:
			return self._undefined_count()

	@windowed_feature(out_of_window_value=lambda self: self._undefined_count())
	def add_morph_bound_count(self, token, i):
		orig = token.text(ignore=self._ignore_chars)
		if orig in self._binding_freq_table:
			return self._binding_freq_table[orig].n_bound
		else:
			return self._undefined_count()

	@windowed_feature(out_of_window_value=lambda self: self._undefined_count())
	def add_morph_not_bound_count(self, token, i):
		orig = token.text(ignore=self._ignore_chars)
		if orig in self._binding_freq_table:
			return self._binding_freq_table[orig].n_not_bound
		else:
			return self._undefined_count()

	@windowed_feature(out_of_window_value=lambda self: self._undefined_prob()) # TODO: should this be 0.5?
	def add_morph_prob_bound(self, token, i):
		orig = token.text(ignore=self._ignore_chars)
		if orig in self._binding_freq_table:
			return self._binding_freq_table[orig].p_bound
		else:
			return self._undefined_prob() # TODO: see above

	# the next 3 features: like the 3 above, except for the ith token and its following token combined
	@windowed_feature(out_of_window_value=lambda self: self._undefined_count())
	def add_combined_token_morph_bound_count(self, token, i):
		if i + 1 == len(self._tokens):
			return self._undefined_count()
		next_token = self._tokens[i + 1]
		combined_text = token.text(ignore=self._ignore_chars) + next_token.text(ignore=self._ignore_chars)
		if combined_text in self._binding_freq_table:
			return self._binding_freq_table[combined_text].n_bound
		else:
			return self._undefined_count()

	@windowed_feature(out_of_window_value=lambda self: self._undefined_count())
	def add_combined_token_morph_not_bound_count(self, token, i):
		if i + 1 == len(self._tokens):
			return self._undefined_count()
		next_token = self._tokens[i + 1]
		combined_text = token.text(ignore=self._ignore_chars) + next_token.text(ignore=self._ignore_chars)
		if combined_text in self._binding_freq_table:
			return self._binding_freq_table[combined_text].n_not_bound
		else:
			return self._undefined_count()

	@windowed_feature(out_of_window_value=lambda self: self._undefined_prob()) #TODO: see above
	def add_combined_token_morph_prob_bound(self, token, i):
		if i + 1 == len(self._tokens):
			return self._undefined_prob() #TODO: see above
		next_token = self._tokens[i + 1]
		combined_text = token.text(ignore=self._ignore_chars) + next_token.text(ignore=self._ignore_chars)
		if combined_text in self._binding_freq_table:
			return self._binding_freq_table[combined_text].p_bound
		else:
			return self._undefined_prob() #TODO: see above

	@windowed_feature(out_of_window_value=lambda self: self._undefined_count())
	def add_length(self, token, i):
		return len(token.text(ignore=self._ignore_chars))

	@windowed_feature(out_of_window_value=lambda self: self._pos_encoder.transform_single(UNKNOWN_POS))
	def add_pos(self, token, i):
		orig = token.text(ignore=self._ignore_chars)
		pos = self._pos_table[orig] if orig in self._pos_table else UNKNOWN_POS
		feature = self._pos_encoder.transform_single(pos if pos in self._pos_vocab else UNKNOWN_POS)
		return feature

	@windowed_feature(out_of_window_value=lambda self: self._undefined_count())
	def add_is_prep(self, token, i):
		orig = token.text(ignore=self._ignore_chars)
		pos = self._pos_table[orig] if orig in self._pos_table else UNKNOWN_POS
		return 1 if "PREP" in pos else 0

	@windowed_feature(out_of_window_value=lambda self: self._char_encoder.transform_single(UNKNOWN_CHAR))
	def add_first_letter(self, token, i):
		orig = token.text(ignore=self._ignore_chars)
		return self._char_encoder.transform_single(orig[0] if orig[0] in self._char_vocab else UNKNOWN_CHAR)

	@windowed_feature(out_of_window_value=lambda self: self._char_encoder.transform_single(UNKNOWN_CHAR))
	def add_last_letter(self, token, i):
		orig = token.text(ignore=self._ignore_chars)
		return self._char_encoder.transform_single(orig[-1] if orig[-1] in self._char_vocab else UNKNOWN_CHAR)

	@windowed_feature(out_of_window_value
					  =lambda self: (self._pos_encoder.transform_single(UNKNOWN_POS)
									 + [self._undefined_prob(),
										#self._undefined_count(),
										#self._undefined_count(),
										#self._undefined_prob()
										]))
	def add_right_substr_pos(self, token, i):
		orig = token.text(ignore=self._ignore_chars)

		j = 1
		pos = UNKNOWN_POS
		while j <= len(orig):
			substr = orig[j:]
			if substr in self._pos_table:
				pos = self._pos_table[substr]
				break
			j += 1

		feats = (
			self._pos_encoder.transform_single(pos if pos in self._pos_vocab else UNKNOWN_POS)
			+ [float(len(substr)) / len(orig)]
		)

		#if substr in self._binding_freq_table:
		#	entry = self._binding_freq_table[substr]
		#	feats += [
		#		entry.n_bound,
		#		entry.n_not_bound,
		#		entry.p_bound
		#	]
		#else:
		#	feats += [self._undefined_count(), self._undefined_count(), self._undefined_prob()]

		return feats

	@windowed_feature(out_of_window_value
					  =lambda self: (self._pos_encoder.transform_single(UNKNOWN_POS)
									 + [self._undefined_prob(),
										#self._undefined_count(),
										#self._undefined_count(),
										#self._undefined_prob()
										]))
	def add_left_substr_pos(self, token, i):
		orig = token.text(ignore=self._ignore_chars)

		j = len(orig) - 1
		pos = UNKNOWN_POS
		while j >= 0:
			substr = orig[:j]
			if substr in self._pos_table:
				pos = self._pos_table[substr]
				break
			j -= 1

		feats = (
			self._pos_encoder.transform_single(pos if pos in self._pos_vocab else UNKNOWN_POS)
			+ [float(len(substr)) / len(orig)]
		)

		#if substr in self._binding_freq_table:
		#	entry = self._binding_freq_table[substr]
		#	feats += [
		#		entry.n_bound,
		#		entry.n_not_bound,
		#		entry.p_bound
		#	]
		#else:
		#	feats += [self._undefined_count(), self._undefined_count(), self._undefined_prob()]

		return feats

	@windowed_feature(out_of_window_value=lambda self: self._undefined_count())
	def add_auto_norm_response(self, token, i):
		if i + 1 == len(self._tokens):
			return self._undefined_count()
		resp = self._normalizer_responses[i]
		return 1 if resp != '?' else 0

	@windowed_feature(out_of_window_value=lambda self: self._undefined_count())
	def add_all_punct(self, token, i):
		return 1 if all(uni.category(c)[0] == "P" for c in token.orig) else 0

	@windowed_feature(out_of_window_value=lambda self: self._undefined_count())
	def add_any_punct(self, token, i):
		return 1 if any(uni.category(c)[0] == "P" for c in token.orig) else 0
