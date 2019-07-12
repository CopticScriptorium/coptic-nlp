from __future__ import division

import numpy as np
from sklearn.linear_model import LogisticRegression

from .tokenizer import Tokenizer
from .featurizer import Featurizer
from .postprocessor import Postprocessor


class LogisticBindingModel:
	def __init__(
		self,
		ignore_chars=[],
		n_groups_left=1,
		n_groups_right=2,
		gold_token_separator="_",
		orig_token_separator=" ",
		binding_freq_file_path=None,
	):
		self._tokens = []
		self._tokenizer = Tokenizer(
			gold_token_separator=gold_token_separator,
			orig_token_separator=orig_token_separator,
			ignore_chars=ignore_chars,
			lowercase=True
		)
		self._featurizer = Featurizer(
			# seps might occur in tokens, also add them to the ignore list
			ignore_chars=ignore_chars + [orig_token_separator, gold_token_separator],
			n_groups_left=n_groups_left,
			n_groups_right=n_groups_right,
			orig_token_separator=" ",
			binding_freq_file_path=binding_freq_file_path,
		)
		self._postprocessor = Postprocessor(separator=gold_token_separator)

		self._m = LogisticRegression(random_state=0, solver='liblinear')

	def _build_feature_matrix(self, text, orig_text=None, training=False):
		"""Prepare X matrix for input to the model. text is gold if orig_text is
		not none, else it is orig"""

		tokens = self._tokenizer.tokenize(text, orig=orig_text)
		self._tokens = tokens
		X = np.array(
			self._featurizer
				.load_tokens(tokens)
				.add_bound_count()
				.add_not_bound_count()
				.add_prob_bound()
				.features()
		)

		return X

	def _build_label_vector(self):
		return np.array(
			self._featurizer
				.load_tokens(self._tokens)
				.labels()
		)

	def train(self, gold_text, orig_text=None):
		X = self._build_feature_matrix(gold_text, orig_text=orig_text, training=True)
		y = self._build_label_vector()
		self._m.fit(X, y)

	def predict(self, orig_text):
		X = self._build_feature_matrix(orig_text, training=False)
		preds = self._m.predict(X).tolist()
		output = self._postprocessor.insert_separators(self._tokens, preds)
		return output





