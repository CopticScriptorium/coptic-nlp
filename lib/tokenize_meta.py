#!/usr/bin/python
#  -*- coding: utf-8 -*-


from __future__ import unicode_literals
import sys, re, io, os
from six import iterkeys, itervalues
PY3 = sys.version_info[0] == 3
from random import shuffle, seed
try:
	from .tokenize_fs import fs_tokenize
	from .tokenize_rf import RFTokenizer
except:
	from tokenize_fs import fs_tokenize
	from tokenize_rf import RFTokenizer

from argparse import ArgumentParser
from six import iteritems
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
import joblib
import numpy as np

seed(42)
np.random.seed(42)

if not PY3:
	reload(sys)
	sys.setdefaultencoding('utf8')

sys.path.append("lib")
script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep


class MetaTokenizer:

	def __init__(self,model="cop",wd=None,rf_tok=None):
		if wd is None:
			self.wd = script_dir + ".." + os.sep + "data" + os.sep
		else:
			self.wd = wd
		self.model = model
		if rf_tok is None:
			self.rf_tok = RFTokenizer(model=self.model)
			self.rf_tok.load()
		else:
			self.rf_tok = rf_tok
		if os.path.isfile(self.wd+"metatok_"+self.model+".mt" + str(sys.version_info[0])):
			self.clf = joblib.load(self.wd+"metatok_"+self.model+".mt" + str(sys.version_info[0]))
		else:
			self.clf = None

	@staticmethod
	def data2list(data):

		gold = None
		if isinstance(data,list):  # List of plain/gold pairs
			pass
			gold = data
		elif len(data) < 100: # Filename?
			if os.path.isfile(data):
				lines = io.open(data,encoding="utf8").read().strip().replace("\r","").split("\n")
				gold = [line.split("\t") for line in lines if line.count("\t") == 1]
			else:
				raise IOError("No file found at: " + data+"\n")
		if gold is None:  # String
			lines = data.strip().replace("\r","").split("\n")
			if "\t" in data:
				gold = [line.split("\t") for line in lines if line.count("\t") == 1]
			else:
				gold = lines

		if gold is None:
			raise IOError("ERR: Invalid gold data\n")

		plain = [g[0] for g in gold]

		return plain, gold

	def featurize(self,plain,gold=None,tokenizations=False):
		rf_tokenizations, min_probas = self.rf_tok.rf_tokenize(plain,proba=True)
		fs_tokenizations, rules_nums = fs_tokenize(plain,rule_nums=True)

		assert len(rf_tokenizations) == len(fs_tokenizations)

		features = []
		vowel_letters = set(["ⲁ","ⲉ","ⲓ","ⲟ","ⲩ","ⲏ","ⲱ"])
		for i, fs_resp in enumerate(fs_tokenizations):
			grp = fs_resp.replace("|","")
			#rf_resp = rf_tokenizations[i]
			#agree = int(rf_resp == fs_resp)
			pipes_fs = fs_resp.count("|")
			#pipes_rf = rf_resp.count("|")
			#proba = min_probas[i]
			rule_num = rules_nums[i]
			first = ord(fs_resp[0])
			last = ord(fs_resp[-1])
			next_first_vowel = 0
			next_last_vowel = 0
			next_first_cons = 0
			next_last_cons = 0
			vowels = []
			cons = []
			if len(grp) > 2:
				for c in grp[1:-1]:
					if c in vowel_letters:
						vowels.append(c)
					else:
						cons.append(c)
				if len(vowels)>0:
					next_first_vowel = ord(vowels[0])
					next_last_vowel = ord(vowels[-1])
				if len(cons)>0:
					next_first_cons = ord(cons[0])
					next_last_cons = ord(cons[-1])
			#feat = [len(grp),agree,proba,pipes_fs,pipes_rf,rule_num,first,last,next_first_vowel,next_last_vowel,next_first_cons,next_last_cons]
			feat = [len(grp),pipes_fs,rule_num,first,last,next_first_vowel,next_last_vowel,next_first_cons,next_last_cons]
			features.append(feat)

		if tokenizations:
			return features, rf_tokenizations
		elif gold is not None:
			y = [fs_tokenizations[i] == gold[i][1] for i in range(len(gold))]
			return features, y
		else:
			return features

	def train(self,data,test_proportion=0.1):

		plain, gold = self.data2list(data)

		# Get estimator responses

		features, y = self.featurize(plain,gold)

		clf = XGBClassifier(random_state=42,nthread=3,colsample_bytree=1.0,max_depth=20)

		indices = list(range(len(gold)))
		shuffle(indices)
		cut = int(len(gold)*test_proportion)
		if test_proportion>0:
			test_indices = indices[0:cut]
			train_indices = indices[cut:]
		else:
			train_indices = indices
			test_indices = []

		train_X = [features[i] for i in train_indices]
		test_X = [features[i] for i in test_indices]
		train_y = [y[i] for i in train_indices]
		test_y = [y[i] for i in test_indices]

		X = np.array(train_X)
		y = np.array(train_y)

		clf.fit(X,y)
		self.clf = clf

		if test_proportion > 0:
			test_X = np.array(test_X)
			test_y = np.array(test_y)

			preds = self.clf.predict(test_X)

			print("Accuracy: ")
			print(accuracy_score(test_y,preds))
		else:
			print("Test proportion is 0, skipping test")

		joblib.dump(clf,self.wd+"metatok_"+self.model+".mt" + str(sys.version_info[0]),compress=3)

	def predict(self,groups):

		features, fs_tokenizations  = self.featurize(groups,tokenizations=True)

		X = np.array(features)
		#preds = self.clf.predict(X)
		probas = self.clf.predict_proba(X)
		probas = [p[1] for p in probas]
		preds = [p>0.5 for p in probas]
		output = []
		for i, pred in enumerate(preds):
			if pred:
				output.append(fs_tokenizations[i])
			else:
				output.append(fs_tokenizations[i])
		return output, preds, probas


if __name__ == "__main__":
	met = MetaTokenizer(model="cop")
	met.train("C:\\Uni\\Coptic\\git\\coptic-nlp\\eval\\_tmp_train.tab",test_proportion=0.0)
	plain, gold = met.data2list("C:\\Uni\\Coptic\\git\\coptic-nlp\\eval\\_tmp_test_onno.tab")
	#plain = [g[0] for g in gold]
	_, y = met.featurize(plain,gold)
	_, preds, _ = met.predict(plain)
	print("Accuracy: ")
	print(accuracy_score(y,preds))
