import os
import io

from .const import OUT_OF_BOUNDS, UNK


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


class Featurizer:
	"""Produces token-level featurizations."""
	def __init__(
			self,
			ignore_chars=[],
			n_groups_left=1,
			n_groups_right=2,
			orig_token_separator=" ",
			binding_freq_file_path=None,
	):
		self._ignore_chars = ignore_chars
		self._n_groups_left = n_groups_left
		self._n_groups_right = n_groups_right
		self._orig_token_separator = orig_token_separator
		self._binding_freq_table = read_binding_freq_file(binding_freq_file_path)

		self._tokens = []
		self._feats = []

	def load_tokens(self, tokens):
		self._tokens = tokens

		# initialize a feature list for each token
		self._feats = []
		for i in range(len(tokens)):
			self._feats.append([])

		return self

	def features(self):
		return self._feats

	def labels(self):
		return [1 if t.gold_bound else 0 for t in self._tokens]

	def add_bound_count(self):
		for i, tok in enumerate(self._tokens):
			orig = tok.text(ignore=self._ignore_chars)
			if orig in self._binding_freq_table:
				self._feats[i].append(self._binding_freq_table[orig].n_bound)
			else:
				self._feats[i].append(0)

		return self

	def add_not_bound_count(self):
		for i, tok in enumerate(self._tokens):
			orig = tok.text(ignore=self._ignore_chars)
			if orig in self._binding_freq_table:
				self._feats[i].append(self._binding_freq_table[orig].n_not_bound)
			else:
				self._feats[i].append(0)

		return self

	def add_prob_bound(self):
		for i, tok in enumerate(self._tokens):
			orig = tok.text(ignore=self._ignore_chars)
			if orig in self._binding_freq_table:
				self._feats[i].append(self._binding_freq_table[orig].p_bound)
			else:
				self._feats[i].append(0.5) # TODO: better way to handle nulls?

		return self
