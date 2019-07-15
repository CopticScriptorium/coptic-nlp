from __future__ import division

import numpy as np
from xgboost import XGBClassifier

from .tokenizer import Tokenizer
from .featurizer import Featurizer
from .postprocessor import Postprocessor


class XGBoostBindingModel:
	def __init__(
		self,
		ignore_chars=[],
		n_groups_left=2,
		n_groups_right=4,
		gold_token_separator="_",
		orig_token_separator=" ",
		binding_freq_file_path=None,
		pos_file_path=None,
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
			pos_file_path=pos_file_path,
			encoder='label'
		)
		self._postprocessor = Postprocessor(separator=gold_token_separator)

		self._m = XGBClassifier()

	def _build_feature_matrix(self, text, orig_text=None, training=False):
		"""Prepare X matrix for input to the model. text is gold if orig_text is
		not none, else it is orig"""

		tokens = self._tokenizer.tokenize(text, orig=orig_text)
		self._tokens = tokens
		X = np.array(
			self._featurizer
				.load_tokens(tokens, training=training)
				.add_bound_count()
				.add_not_bound_count()
				.add_prob_bound(n_groups_left=1, n_groups_right=2)
				.add_combined_token_bound_count(n_groups_left=1, n_groups_right=1)
				.add_combined_token_not_bound_count(n_groups_left=1, n_groups_right=1)
				.add_combined_token_prob_bound(n_groups_left=1, n_groups_right=1)
				.add_length(n_groups_left=2, n_groups_right=4)
				.add_pos(n_groups_left=1, n_groups_right=2)
				.add_first_letter(n_groups_left=0, n_groups_right=1)
				.add_last_letter(n_groups_left=1, n_groups_right=0)
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
		X = self._build_feature_matrix(orig_text)
		preds = self._m.predict(X).tolist()
		output = self._postprocessor.insert_separators(self._tokens, preds)
		return output





