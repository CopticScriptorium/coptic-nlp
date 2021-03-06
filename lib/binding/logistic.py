from __future__ import division

import numpy as np
from sklearn.linear_model import LogisticRegressionCV
from sklearn.svm import LinearSVC

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
		ngram_binding_freq_file_path=None,
		pos_file_path=None,
		group_freq_file_path=None,
	):
		self._tokens = []
		self._tokenizer = Tokenizer(
			gold_token_separator=gold_token_separator,
			orig_token_separator=orig_token_separator,
			ignore_chars=ignore_chars,
			lowercase=True
		)
		self._featurizer = Featurizer(
			n_groups_left,
			n_groups_right,
			# seps might occur in tokens, also add them to the ignore list
			ignore_chars=ignore_chars + [orig_token_separator, gold_token_separator],
			orig_token_separator=" ",
			binding_freq_file_path=binding_freq_file_path,
			ngram_binding_freq_file_path=ngram_binding_freq_file_path,
			pos_file_path=pos_file_path,
			group_freq_file_path=group_freq_file_path,
			encoder='one_hot'
		)
		self._postprocessor = Postprocessor(separator=gold_token_separator)

		self._m = LogisticRegressionCV(
			random_state=0,
			fit_intercept=True,
			max_iter=100,
			solver='liblinear',
			penalty='l2',
			cv=3
		)

	def _build_feature_matrix(self, text, orig_text=None, training=False):
		"""Prepare X matrix for input to the model. text is gold if orig_text is
		not none, else it is orig"""

		tokens = self._tokenizer.tokenize(text, orig=orig_text)
		self._tokens = tokens
		X = np.array(
			self._featurizer
				.load_tokens(tokens, training=training)
				.add_group_count()
				.add_combined_token_group_count()
				#.add_morph_bound_count()
				#.add_morph_not_bound_count()
				#.add_morph_prob_bound()
				#.add_combined_token_morph_bound_count()
				#.add_combined_token_morph_not_bound_count()
				#.add_combined_token_morph_prob_bound()
				.add_length(left=1, right=2)
				.add_pos(left=1, right=2)
				#.add_is_prep(left=0, right=1)
				.add_first_letter(left=0, right=1)
				.add_last_letter(left=1, right=0)
				.add_right_substr_pos(left=1, right=0)
				.add_left_substr_pos(left=0, right=1)
				.add_auto_norm_response(left=1, right=0)
				.add_all_punct(left=0, right=1)
				#.add_any_punct(left=1, right=1)
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





