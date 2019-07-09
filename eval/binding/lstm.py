from __future__ import division

import numpy as np
from keras import backend as K
from keras import metrics, optimizers
from keras.models import Sequential, Model
from keras.layers import Embedding, Bidirectional, LSTM, Dense, TimeDistributed, Dropout, Input
from keras.callbacks import EarlyStopping
from keras.utils import to_categorical
from tensorflow import logging
logging.set_verbosity(logging.ERROR)

OUT_OF_BOUNDS = "ॐ"
UNK = "<UNK>"


class LSTMBindingModel:
	def __init__(self,
				 n_chars_left=25,
				 n_chars_right=25,
				 sample_ratio=None,
				 gold_token_separator="_",
				 pred_token_separator=" ",
				 embedding_size=100,
				 hidden_size=10,
				 dropout=0.2,
				 epochs=10
				 ):
		assert n_chars_left >= 0 and type(n_chars_left) == int
		assert n_chars_right >= 0 and type(n_chars_right) == int
		assert sample_ratio is None or 0 <= sample_ratio <= 1
		assert type(gold_token_separator) == str
		assert type(pred_token_separator) == str
		self._n_chars_left = n_chars_left
		self._n_chars_right = n_chars_right
		self._sample_ratio = sample_ratio
		self._gold_token_separator = gold_token_separator
		self._pred_token_separator = pred_token_separator
		self._separators = [gold_token_separator, pred_token_separator]

		self._embedding_size = embedding_size
		self._hidden_size = hidden_size
		self._dropout = dropout
		self._epochs = epochs

		self._indices = None
		self._char_vocab = None

	def _generate_sample_indices(self, n):
		"""Samples without replacement in the interval [0, n-1] until n * self._sample_ratio indices have been drawn.
		If self._sample_ratio is None, returns the entire interval.
		:param n: the length of the text
		:return: a list of indexes into the text
		"""
		if self._sample_ratio is None:
			return list(reversed(range(n)))

		raise Exception("Random sampling not currently supported")

		#sampled_indices = []
		#indices = list(enumerate(range(n)))
		#while len(sampled_indices) / n < self._sample_ratio:
		#	list_index, i = random.choice(indices)
		#	indices.pop(list_index)
		#	sampled_indices.append(i)

		#return list(reversed(sorted(sampled_indices)))

	@staticmethod
	def featurize_char(char):
		return [1 if c == char else 0 for c in self._char_vocab]

	def _take_left_n_chars(self, txt, i):
		"""Takes the self._n_chars_left that lie to the left of txt[i], IGNORING SEPARATORS. Does not include txt[i].
		A padding character is used if i is too close to the beginning of txt."""
		assert 0 <= i <= len(txt)

		chars = []
		k = i
		while len(chars) < self._n_chars_left and k >= 0:
			c = txt[k]
			if c not in self._separators:
				chars.append(c)
			k -= 1
		s = "".join(chars)
		return OUT_OF_BOUNDS * (self._n_chars_left - len(s)) + s

	def _take_right_n_chars(self, txt, i):
		"""Takes the self._n_chars_right that lie to the right of txt[i], IGNORING SEPARATORS. Does not include txt[i].
		A padding character is used if i is too close to the beginning of txt."""
		assert 0 <= i <= len(txt)

		chars = []
		k = i
		while len(chars) < self._n_chars_right and k < len(txt):
			c = txt[k]
			if c not in self._separators:
				chars.append(c)
			k += 1
		s = "".join(chars)
		return s + OUT_OF_BOUNDS * (self._n_chars_right - len(s))

	def _featurize_at_i(self, txt, i):
		"""Transforms the position i in a text into a row in the matrix that will be fed to the model."""
		feats = []
		feats += [self.featurize_char(c) for c in self._take_left_n_chars(txt, i)]
		feats.append(self.featurize_char(txt[i]))
		feats += [self.featurize_char(c) for c in self._take_right_n_chars(txt, i)]

		return np.array(feats)

	def _boundary_after_i(self, gold_txt, i):
		"""Check an index in gold text to see if it is immediately followed by a boundary."""
		boundary = (i == len(gold_txt) - 1  # if it's the end of the text, we should predict a boundary
					or gold_txt[i + 1] == self._gold_token_separator)
		return 1 if boundary else 0

	def _matrixify(self, txt, training=True):
		"""Prepare X matrix for input to the model, and the y binary label matrix if we are not training
		(i.e., predicting)"""
		indices = self._generate_sample_indices(len(txt)) #if training else self._indices
		self._indices = indices
		char_vocab = list(set(txt).difference(set(self._separators))) if training else self._char_vocab

		X = np.array([self._featurize_at_i(txt, i, char_vocab) for i in indices])
		if not training:
			return X

		self._char_vocab = char_vocab
		y = np.array([self._boundary_after_i(txt, i) for i in indices])
		return X, y

	def _construct_model(self):
		model = Sequential()
		model.add(Embedding(len(self._char_vocab), self._embedding_size))
		model.add(Dropout(self._dropout))
		model.add(Bidirectional(LSTM(self._hidden_size)))
		model.add(Dropout(self._dropout))
		model.add(Dense(2, activation='softmax'))

		adadelta = optimizers.Adadelta(clipnorm=1.0)
		model.compile(optimizer=adadelta, loss='categorical_crossentropy', metrics=['accuracy'])

		self._m = model

	def train(self, txt):
		assert self._pred_token_separator not in txt

		X, y = self._matrixify(txt, training=True)
		self._construct_model()
		self._m.fit(X, y)

	def _insert_separators(self, txt, preds):
		indices = self._indices
		assert indices is not None and monotonic_decreasing(indices)

		for k, pred in enumerate(preds):
			index = indices[k]
			txt = insert_after_index(txt, index, self._gold_token_separator)
		return txt

	def predict(self, txt):
		assert self._gold_token_separator not in txt

		txt = txt.replace(self._pred_token_separator, "")
		X = self._matrixify(txt, training=False)

		preds = self._m.predict(X).tolist()
		return self._insert_separators(txt, preds)


def insert_after_index(s, i, x):
	return s[:i+1] + x + s[i+1:]


def monotonic_decreasing(l):
	b = True
	for i in range(len(l)-1):
		if l[i + 1] > l[i]:
			b = False
	return b

