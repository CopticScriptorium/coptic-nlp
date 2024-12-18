#!/usr/bin/python
# -*- coding: utf-8 -*-

import io, os, sys, re, copy
from collections import defaultdict, Counter
import numpy as np
import pandas as pd
from glob import glob
from argparse import ArgumentParser

import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, classification_report
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from xgboost import XGBClassifier

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
eval_dir = script_dir + ".." + os.sep + "eval" + os.sep
util_dir = eval_dir + "utils" + os.sep
sys.path.append(util_dir[:-1])
sys.path.append(eval_dir[:-1])

from eval.utils.eval_utils import list_files


special = ["·","·","ϥⲥϩⲟⲩⲟⲣⲧ","ϩⲙⲡϫⲟⲉⲓⲥ","ϩⲙⲡⲉⲕⲣⲁⲛ","ϩⲛⲟⲩ","ϩⲱⲱⲛ","ϭⲉ","ⲁϣ","ⲁϥϣⲗⲏⲗ","ⲁⲡⲁ","ⲁⲡⲛⲟⲩⲧⲉ","ⲁⲩϫⲟⲟⲥ","ⲅⲁⲣ","ⲇⲉ","ⲉϣϫⲉ",
		   "ⲉϥϣⲁϫⲉ","ⲉϥϩⲟⲟⲩ","ⲉⲁⲙⲛⲧⲉ","ⲉⲓϫⲱ","ⲉⲓⲧⲁ","ⲉⲡϫⲓⲛϫⲏ","ⲉⲧⲃⲉⲡⲁⲓ","ⲉⲧⲃⲏⲏⲧⲟⲩ","ⲕⲁⲓ","ⲕⲁⲗⲱⲥ","ⲕⲁⲧⲁⲛⲉⲅⲣⲁⲫⲏ","ⲙⲛⲛⲉⲩⲉⲣⲏⲩ","ⲙⲟⲛⲟⲛ",
		   "ⲛϣⲙⲙⲟ","ⲛϫⲓⲟⲩⲉ","ⲛϭⲓⲁⲡⲁ","ⲛϭⲓⲓⲏⲥⲟⲩⲥ","ⲛϭⲓⲡϩⲗⲗⲟ","ⲛϭⲓⲡⲥⲟⲛ","ⲛⲇⲓⲕⲁⲓⲟⲥ","ⲛⲉⲥⲛⲏⲩ","ⲛⲛϣⲏⲣⲉ","ⲛⲧⲁⲡϫⲟⲉⲓⲥ","ⲛⲧⲉⲧⲛⲥⲟⲟⲩⲛ","ⲛⲧⲙⲉ","ⲟⲛ",
		   "ⲟⲩⲛ","ⲡϣⲉ","ⲡⲉϫⲉⲡϩⲗⲗⲟ","ⲡⲉⲥⲧⲁⲩⲣⲟⲥ","ⲡⲥⲱⲙⲁ","ⲧⲉⲧⲛⲏⲡ","ⲻ",",",".",":","[...]"]
special = ["·","·","ϩⲱⲱϥ","ϩⲱⲱⲛ","ϭⲉ","ⲁϣ","ⲁⲡⲁ","ⲁⲡⲛⲟⲩⲧⲉ","ⲁⲩϫⲟⲟⲥ","ⲅⲁⲣ","ⲇⲉ","ⲉϣϫⲉ","ⲁⲩⲱ","ⲏ","ⲉⲓⲧⲉ","ⲟⲩⲇⲉ",
		   "ⲉϥϣⲁϫⲉ","ⲉϥϩⲟⲟⲩ","ⲉⲁⲙⲛⲧⲉ","ⲉⲓϫⲱ","ⲉⲓⲧⲁ","ⲉⲡϫⲓⲛϫⲏ","ⲉⲧⲃⲉⲡⲁⲓ","ⲉⲧⲃⲏⲏⲧⲟⲩ","ⲕⲁⲓ","ⲕⲁⲛ","ⲕⲁⲧⲁⲛⲉⲅⲣⲁⲫⲏ","ⲙⲟⲛⲟⲛ","ⲟⲩ",
		   "ⲛϭⲓⲁⲡⲁ","ⲛϭⲓⲓⲏⲥⲟⲩⲥ","ⲛϭⲓⲡϩⲗⲗⲟ","ⲛϭⲓⲡⲥⲟⲛ","ⲛⲇⲓⲕⲁⲓⲟⲥ","ⲛⲉⲥⲛⲏⲩ","ⲛⲛϣⲏⲣⲉ","ⲛⲧⲁⲡϫⲟⲉⲓⲥ","ⲟⲛ",
		   "ⲟⲩⲛ","ⲙⲉⲛ","ⲡⲉϫⲁϥ","ⲡⲉϫⲁⲓ","ⲁϥϫⲟⲟⲥ","ⲻ",",",".",":","[...]","ⲉϩⲣⲁⲓ","ⲉϩⲟⲩⲛ","ⲉⲃⲟⲗ"]#,"ⲧⲏⲣⲟⲩ","ⲛⲓⲙ","ⲁⲛ","ⲛⲁⲓ","ⲡⲁⲓ","ⲡⲉ","ⲛⲉ"]
special = ["·","ϭⲉ","ⲁϣ","ⲅⲁⲣ","ⲇⲉ","ⲉϣϫⲉ","ⲁⲩⲱ","ⲏ","ⲉⲓⲧⲉ","ⲟⲩⲇⲉ",
		  "ⲅⲁⲣ","ⲕⲁⲓ","ⲕⲁⲛ","ⲟⲩ","ⲛⲧⲟϥ","ⲡⲉ","ⲛⲉ",
		   "ⲟⲛ","ⲁⲣⲁ","ⲁⲛ","ⲛⲓⲙ","ⲙⲏ","ⲙⲟⲛⲟⲛ","ϣⲟⲣⲡ",
		   "ⲟⲩⲛ","ⲙⲉⲛ","ⲡⲉϫⲁϥ","ⲡⲉϫⲁⲓ","ⲁϥϫⲟⲟⲥ","ⲉϩⲣⲁⲓ","ⲉϩⲟⲩⲛ","ⲉⲃⲟⲗ"]#,"ⲧⲏⲣⲟⲩ","ⲛⲓⲙ","ⲁⲛ","ⲛⲁⲓ","ⲡⲁⲓ","ⲡⲉ","ⲛⲉ"]
wack = ["ⲅⲁⲣ","ⲇⲉ","ⲙⲉⲛ","ⲟⲛ","ⲟⲩⲛ","ϭⲉ"]


def get_case(word,ekthetic=0):
	if ekthetic > 0:
		return "t"
	elif word.isdigit():
		return "d"
	elif word.isupper():
		return "u"
	elif word.islower():
		return "l"
	elif word.istitle():
		return "t"
	else:
		return "o"


class BGSentencer:

	def __init__(self):
		pass

	def read_sgml(self,data,element="translation", genre="other"):

		lines = data.strip().replace("\r","\n").split("\n")
		output = []
		feats = {}
		pos = []
		norms = []
		dist2punct = 0
		dist2wack = 0
		dist2je = 0
		boundary=1
		tok_id = 0
		vocab = defaultdict(int)
		vocab_parts = defaultdict(int)
		words = []
		firsts = set([])
		lasts = set([])
		ekthetic = 0
		genre = "other"
		for line in lines:
			if 'corpus=' in line and genre is None:
				corpus = re.search(r'corpus="([^"]*)"',line).group(1)
				if "shenoute" in corpus or "besa" in corpus:
					genre = "sermon"
				elif "apophthegmata" in corpus:
					genre = "ap"
				elif corpus.startswith("sahidic"):
					genre = "bible"
				else:
					genre = "other"
			if "ekthetic" in line:
				ekthetic = 1
			if 'orig_group="' in line:
				orig_group = re.search(r'orig_group="([^"]*)"',line).group(1)
			if 'norm_group="' in line:
				norm_group = re.search(r'norm_group="([^"]*)"',line).group(1)
			if 'pos=' in line:
				tag = re.search(r'pos="([^"]*)"',line).group(1)
				pos.append(tag)
			if 'norm=' in line:
				norm = re.search(r'norm="([^"]*)"',line).group(1)
				norms.append(norm)
				vocab_parts[norm] +=1
			if '</norm_group>' in line:
				dist2punct += 1
				tok_id+=1
				#feats = {"lpos":pos[0],"rpos":pos[-1],"parts":len(pos),"first":norm_group[0],"last":norm_group[-1],
				#			  "len":len(norm_group),"case":get_case(orig_group,ekthetic),"dist2punct":dist2punct,
				#			  "bg":norm_group,"genre":genre,"label":boundary}
				feats = {"lpos":pos[0],"rpos":pos[-1],"parts":len(pos),"first":norm_group[0],"last":norm_group[-1],
							  "len":len(norm_group),"case":get_case(orig_group),"dist2punct":dist2punct,
							  "bg":norm_group,"genre":genre,"label":boundary,"lnorm":norms[0],"dist2wack":dist2wack,
						 "dist2je":dist2je,"tok_id":tok_id}
				ekthetic = 0
				boundary = 0
				words.append(norm_group)
				output.append(feats)
				if pos[0] == "PUNCT":
					dist2punct = 0
				if norm_group in wack:
					dist2wack = 0
				if norm_group == "ϫⲉ":
					dist2je = 0
				dist2wack +=1
				dist2je += 1
				vocab[norm_group] += 1
				firsts.add(norm_group[0])
				lasts.add(norm_group[-1])
				pos = []
			if "</"+element+">" in line:  # Next unit is sentence initial
				boundary = 1

		dist2punct = 5
		dist2je = 5
		dist2wack = 5
		for row in output[::-1]:
			if row["lpos"] == "PUNCT":
				dist2punct = 0
			if row["bg"] in wack:
				dist2wack = 0
			if row["lnorm"] == "ϫⲉ":
				dist2je = 0
			row["nextpunct"] = dist2punct
			row["nextje"] = dist2je
			row["nextwack"] = dist2wack
			dist2punct+=1
			dist2wack+=1
			dist2je+=1

		return output, vocab, vocab_parts, firsts, lasts, words

	def read_conll(self,data):

		lines = data.strip().replace("\r","\n").split("\n")
		output = []
		feats = {}
		pos = []
		norms = []
		dist2punct = 0
		dist2wack = 0
		dist2je = 0
		tok_id = 0
		boundary=1
		vocab = defaultdict(int)
		vocab_parts = defaultdict(int)
		firsts = set([])
		lasts = set([])
		orig_group = norm_group = ""
		superspan = 0
		misc = "_"
		genre = "other"
		words = []
		for line in lines:
			if 'newdoc' in line:
				corpus = re.search(r' ([^ ]+):',line).group(1)
				if "shenoute" in corpus or "besa" in corpus:
					genre = "sermon"
				elif "apophthegmata" in corpus:
					genre = "ap"
				elif corpus.startswith("sahidic"):
					genre = "bible"
				else:
					genre = "other"
			if '\t' in line:
				tid, word, lemma, upos, xpos, morph, head, func, _, misc = line.split("\t")
				if '-' in tid:
					s,e  = tid.split("-")
					superspan = int(e)-int(s)+1
					continue
			elif len(line.strip()) == 0:  # Next unit is sentence initial
				boundary = 1
				continue
			elif line.startswith("#"):
				continue

			if 'Orig=' in misc:
				orig = re.search(r'Orig=([^|]*)',misc).group(1)
				orig_group += orig
			else:
				orig += word
			norm_group += word
			vocab_parts[word] += 1
			norms.append(word)
			superspan -= 1  # Seen a word, down-tick superspan

			if xpos != "_":
				pos.append(xpos)
				dist2punct += 1
			if superspan <= 0:
				tok_id +=1
				feats = {"lpos":pos[0],"rpos":pos[-1],"parts":len(pos),"first":norm_group[0],"last":norm_group[-1],
							  "len":len(norm_group),"case":get_case(orig_group),"dist2punct":dist2punct,
							  "bg":norm_group,"genre":genre,"label":boundary,"lnorm":norms[0],"dist2wack":dist2wack,
						 "dist2je":dist2je,"tok_id":tok_id}
				boundary = 0
				output.append(feats)
				if pos[0] == "PUNCT":
					dist2punct = 0
				if norms[0] == "ϫⲉ":
					dist2je = 0
				if norm_group in wack:
					dist2wack = 0
				vocab[norm_group] += 1
				firsts.add(norm_group[0])
				lasts.add(norm_group[-1])
				pos = []
				norms = []
				words.append(norm_group)
				dist2wack +=1
				dist2je += 1
				norm_group = ""
				orig_group = ""
		dist2punct = 5
		dist2je = 5
		dist2wack = 5
		for row in output[::-1]:
			if row["lpos"] == "PUNCT":
				dist2punct = 0
			if row["bg"] in wack:
				dist2wack = 0
			if row["lnorm"] == "ϫⲉ":
				dist2je = 0
			row["nextpunct"] = dist2punct
			row["nextje"] = dist2je
			row["nextwack"] = dist2wack
			dist2punct+=1
			dist2wack+=1
			dist2je+=1

		return output, vocab, vocab_parts, firsts, lasts, words


	def train(self, training, element="translation", format="conll", model_path=None, rare_thresh=100):
		"""
		Train the EnsembleSentencer. Note that the underlying estimators are assumed to be pretrained already.

		:param training: File or list of files in TTSGML with <element> span delimiting sentences
		:return: None
		"""


		if not isinstance(training,list):
			training = [training]

		train = ""
		from random import shuffle, seed
		seed(42)
		shuffle(training)
		for file_ in training:
			text = io.open(file_,encoding="utf8").read().strip().replace("\r","") + "\n"
			if "</" + element in text or format == "conll":
				if element + '="..."' in text:
					keep = []
					sents = text.split("</" + element +">")
					for sent in sents:
						if element + '="..."' in sent:
							continue
						keep.append(sent)
					text = "</" + element + ">".join(keep)
					if len(keep) == 0 or element + " " +element+"=" not in text:
						continue
				train+=text
			else:
				sys.stderr.write("! Skipping SGML file " + os.path.basename(file_) + ": no " +element)


		if model_path is None:  # Try default model location
			model_path = script_dir + "cop_sent.pkl"

		cat_labels = ["lpos","rpos","bg","case","genre","first","lnorm"]  # "first","last","case"
		num_labels = ["len","dist2punct","nextpunct","parts","nextwack","tok_id"]#,"nextje"]#,"dist2je"]

		if format == "sgml":
			train_feats, vocab, vocab_parts, firsts, lasts, words = self.read_sgml(train,element=element)
		else:
			train_feats, vocab, vocab_parts, firsts, lasts, words = self.read_conll(train)

		# Ensure that "_" is in the possible values of first/last for OOV chars at test time
		oov_item = train_feats[-1]
		oov_item["first"] = "_"
		oov_item["last"] = "_"
		oov_item["bg"] = "_"
		oov_item["lpos"] = "_"
		oov_item["rpos"] = "_"
		train_feats.append(oov_item)
		train_feats = [oov_item] + train_feats

		vocab = Counter(vocab)
		top_n_words = vocab.most_common(rare_thresh)
		top_n_words, _ = zip(*top_n_words)
		vocab_parts = Counter(vocab_parts)
		top_n_parts = vocab_parts.most_common(rare_thresh)
		top_n_parts, _ = zip(*top_n_parts)


		# Hard coded special list of preferred lexical items
		top_n_words = special

		headers = sorted(list(train_feats[0].keys()))
		data = []

		for i, item in enumerate(train_feats):
			if item["bg"] in wack and False:
				item["bg"] = "WACK"
			elif item["bg"] not in top_n_words:
				item["bg"] = item["lpos"]
			if item["lnorm"] not in top_n_parts:
				item["lnorm"] = item["lpos"]

			feats = []
			for k in headers:
				feats.append(item[k])

			data.append(feats)

		data, headers, cat_labels, num_labels = self.n_gram(data, headers, cat_labels, num_labels)
		# No need for n_gram feats for the following:
		if "genre_min1" in cat_labels:
			cat_labels.remove("genre_min2")
			cat_labels.remove("genre_min1")
			cat_labels.remove("genre_pls1")
			cat_labels.remove("genre_pls2")
		if "case_min1" in cat_labels:
			cat_labels.remove("case_min2")
			cat_labels.remove("case_min1")
			cat_labels.remove("case_pls1")
			cat_labels.remove("case_pls2")
		if "dist2punct_min1" in num_labels:
			num_labels.remove("dist2punct_min2")
			num_labels.remove("dist2punct_min1")
			num_labels.remove("dist2punct_pls1")
			num_labels.remove("dist2punct_pls2")
		if "nextpunct_min1" in num_labels:
			num_labels.remove("nextpunct_min2")
			num_labels.remove("nextpunct_min1")
			num_labels.remove("nextpunct_pls1")
			num_labels.remove("nextpunct_pls2")
		if "dist2je_min1" in num_labels:
			num_labels.remove("dist2je_min2")
			num_labels.remove("dist2je_min1")
			num_labels.remove("dist2je_pls1")
			num_labels.remove("dist2je_pls2")
		if "nextje_min1" in num_labels:
			num_labels.remove("nextje_min2")
			num_labels.remove("nextje_min1")
			num_labels.remove("nextje_pls1")
			num_labels.remove("nextje_pls2")
		if "dist2wack_min1" in num_labels:
			num_labels.remove("dist2wack_min2")
			num_labels.remove("dist2wack_min1")
			num_labels.remove("dist2wack_pls1")
			num_labels.remove("dist2wack_pls2")
		if "nextwack_min1" in num_labels:
			num_labels.remove("nextwack_min2")
			num_labels.remove("nextwack_min1")
			num_labels.remove("nextwack_pls1")
			num_labels.remove("nextwack_pls2")
		if "tok_id_min1" in num_labels:
			num_labels.remove("tok_id_min2")
			num_labels.remove("tok_id_min1")
			num_labels.remove("tok_id_pls1")
			num_labels.remove("tok_id_pls2")

		# Use specific feature subset
		chosen_feats = None
		if chosen_feats is not None:
			new_cat = []
			new_num = []
			for feat in chosen_feats:
				if feat in cat_labels:
					new_cat.append(feat)
				elif feat in num_labels:
					new_num.append(feat)
			cat_labels = new_cat
			num_labels = new_num

		data = pd.DataFrame(data, columns=headers)
		data_encoded, multicol_dict = self.multicol_fit_transform(data, pd.Index(cat_labels))

		data_x = data_encoded[cat_labels+num_labels]#.values
		data_y = [int(t['label'] == 1) for t in train_feats]

		sys.stderr.write("o Learning...\n")

		tune_mode = None#"val" #None
		if tune_mode is not None:
			# Randomize samples for training
			data_x = data_encoded[cat_labels+num_labels+["label"]]#.sample(frac=1,random_state=42)
			data_y = np.where(data_x['label'] == 0, 0, 1)
			data_x = data_x[cat_labels+num_labels]

			# Reserve 10% for validation
			val_x = data_x[:int(len(data_y)/9)]
			val_y = data_y[:int(len(data_y)/9)]
			data_x = data_x[int(len(data_y)/9):]
			data_y = data_y[int(len(data_y)/9):]


		clf = XGBClassifier(random_state=42, n_jobs=3, colsample_bytree=0.9, eta=0.06, gamma=0.08, max_depth=12, n_estimators=150, subsample=0.75)
		#clf = XGBClassifier(random_state=42, n_jobs=3,max_depth=5,min_child_weight=2)
		#clf = RandomForestClassifier(random_state=42,n_jobs=3,n_estimators=200)
		#clf = AdaBoostClassifier(random_state=42,n_estimators=500,learning_rate=0.1)#,n_estimators=2000)#, n_jobs=3)
		clf.fit(data_x,data_y)

		if tune_mode is not None:
			preds = clf.predict(val_x)
			print(confusion_matrix(val_y,preds))
			print("Precision")
			print(precision_score(val_y,preds))
			print("Recall")
			print(recall_score(val_y,preds))
			print("F score")
			print(f1_score(val_y,preds))
			print(classification_report(val_y,preds))

			feature_names = cat_labels + num_labels

			zipped = zip(feature_names, clf.feature_importances_)
			sorted_zip = sorted(zipped, key=lambda x: x[1], reverse=True)
			sys.stderr.write("o Feature importances:\n\n")
			for name, importance in sorted_zip:
				sys.stderr.write(name + "=" + str(importance) + "\n")

			if hasattr(clf, "oob_score_"):
				sys.stderr.write("\no OOB score: " + str(clf.oob_score_)+"\n")

			output=[]
			for i, word in enumerate(words[:int(len(data_y)/9)-2]):
				gold = str(val_y[i+1])
				pred = str(preds[i+1])
				output.append("\t".join([word,gold,pred]))
			with io.open("sent_preds.tab",'w',encoding="utf8") as f:
				f.write("\n".join(output))
		else:
			feature_names = cat_labels + num_labels

			zipped = zip(feature_names, clf.feature_importances_)
			sorted_zip = sorted(zipped, key=lambda x: x[1], reverse=True)
			sys.stderr.write("o Feature importances:\n\n")
			for name, importance in sorted_zip:
				sys.stderr.write(name + "=" + str(importance) + "\n")

		sys.stderr.write("\no Serializing model...\n")

		joblib.dump((clf, num_labels, cat_labels, multicol_dict, top_n_words, firsts, lasts), model_path, compress=3)

	def predict(self, infile, model_path=None, eval_gold=False, as_text=False, format="sgml", genre="other"):
		"""
		Predict sentence splits using an existing model

		:param infile: File in *.sgml or *.conll format
		:param model_path: Pickled model file, default: <script_dir>/cop_sent.pkl
		:param eval_gold: Whether to score the prediction; only applicable if using a gold .conll file as input
		:param as_text: Boolean, whether the input is a string, rather than a file name to read
		:param format: sgml or conll
		:return: tokenwise binary prediction vector if eval_gold is False, otherwise prints evaluation metrics and diff to gold
		"""

		if model_path is None:  # Try default model location
			model_path = script_dir + "cop_sent.pkl"

		clf, num_labels, cat_labels, multicol_dict, vocab, firsts, lasts = joblib.load(model_path)

		if as_text:
			indata = infile
		else:
			indata = io.open(infile,encoding="utf8").read()

		#tagged = udpipe_tag(conllu,self.udpipe_model)
		#tagged = tt_tag(conllu,self.lang)
		train_feats, _, _, _, _, toks = self.read_sgml(indata,genre=genre)
		headers = sorted(list(train_feats[0].keys()))

		data = []

		preds = {}

		genre_warning = False
		for i, item in enumerate(train_feats):
			item["first"] = item["bg"][0] if item["bg"][0] in firsts else "_"
			item["last"] = item["bg"][-1] if item["bg"][-1] in lasts else "_"
			if "genre" in cat_labels:
				if item["genre"] not in multicol_dict["encoder_dict"]["genre"].classes_:  # New genre not in training data
					if not genre_warning:
						sys.stderr.write("! WARN: Genre not in training data: " + item["genre"] + "; suppressing further warnings\n")
						genre_warning = True
					item["genre"] = "other"
			if "lpos" in cat_labels:
				if item["lpos"] not in multicol_dict["encoder_dict"]["lpos"].classes_:
					item["lpos"] = "_"
			if "rpos" in cat_labels:
				if item["rpos"] not in multicol_dict["encoder_dict"]["rpos"].classes_:
					item["rpos"] = "_"
			if "lnorm" in cat_labels:
				if item["lnorm"] not in multicol_dict["encoder_dict"]["lnorm"].classes_:
					if item["lpos"] in multicol_dict["encoder_dict"]["lnorm"].classes_:
						item["lnorm"] = item["lpos"]
					else:
						item["lnorm"] = "_"
			if "rnorm" in cat_labels:
				if item["rnorm"] not in multicol_dict["encoder_dict"]["rnorm"].classes_:
					if item["rpos"] in multicol_dict["encoder_dict"]["rnorm"].classes_:
						item["rnorm"] = item["rpos"]
					else:
						item["rnorm"] = "_"
			if item["bg"] not in vocab and "bg" in multicol_dict["encoder_dict"]:
				if item["lpos"] in multicol_dict["encoder_dict"]["bg"].classes_:
					item["bg"] = item["lpos"]
				else:
					item["bg"] = "_"

			feats = []
			for k in headers:
				feats.append(item[k])

			data.append(feats)

		data, headers, _, _ = self.n_gram(data,headers,[],[])

		data = pd.DataFrame(data, columns=headers)
		data_encoded = self.multicol_transform(data,columns=multicol_dict["columns"],all_encoders_=multicol_dict["all_encoders_"])

		data_x = data_encoded[cat_labels+num_labels]#.values
		pred = clf.predict(data_x)

		# Ensure first token in document is always a sentence break
		#for i, x in enumerate(data_encoded["tok_id"].values):
		#	if x == 1:
		#		pred[i] = 1

		pred[0] = 1
		for i, x in enumerate(data_encoded["nextwack"].values):
			if x == 1:
				pass
				#pred[i] = 1

		if eval_gold:
			gold_feats, _,_,_,_,_ = self.read_sgml(indata,genre=genre)
			gold = [int(t['label'] == 1) for t in gold_feats]
			conf_mat = confusion_matrix(gold, pred)
			sys.stderr.write(str(conf_mat) + "\n")
			true_positive = conf_mat[1][1]
			false_positive = conf_mat[0][1]
			false_negative = conf_mat[1][0]
			prec = true_positive / (true_positive + false_positive)
			rec = true_positive / (true_positive + false_negative)
			f1 = 2*prec*rec/(prec+rec)
			sys.stderr.write("P: " + str(prec) + "\n")
			sys.stderr.write("R: " + str(rec) + "\n")
			sys.stderr.write("F1: " + str(f1) + "\n")
			with io.open("diff.tab",'w',encoding="utf8") as f:
				for i in range(len(gold)):
					f.write("\t".join([toks[i],str(gold[i]),str(pred[i])])+"\n")
			return conf_mat, prec, rec, f1
		else:
			return pred

	@staticmethod
	def multicol_fit_transform(dframe, columns):
		"""
		Transforms a pandas dataframe's categorical columns into pseudo-ordinal numerical columns and saves the mapping

		:param dframe: pandas dataframe
		:param columns: list of column names with categorical values to be pseudo-ordinalized
		:return: the transformed dataframe and the saved mappings as a dictionary of encoders and labels
		"""

		if isinstance(columns, list):
			columns = np.array(columns)
		else:
			columns = columns

		encoder_dict = {}
		# columns are provided, iterate through and get `classes_` ndarray to hold LabelEncoder().classes_
		# for each column; should match the shape of specified `columns`
		all_classes_ = np.ndarray(shape=columns.shape, dtype=object)
		all_encoders_ = np.ndarray(shape=columns.shape, dtype=object)
		all_labels_ = np.ndarray(shape=columns.shape, dtype=object)
		for idx, column in enumerate(columns):
			# instantiate LabelEncoder
			le = LabelEncoder()
			# fit and transform labels in the column
			dframe.loc[:, column] = le.fit_transform(dframe.loc[:, column].values)
			encoder_dict[column] = le
			# append the `classes_` to our ndarray container
			all_classes_[idx] = (column, np.array(le.classes_.tolist(), dtype=object))
			all_encoders_[idx] = le
			all_labels_[idx] = le

		multicol_dict = {"encoder_dict":encoder_dict, "all_classes_":all_classes_,"all_encoders_":all_encoders_,"columns": columns}
		return dframe, multicol_dict

	@staticmethod
	def multicol_transform(dframe, columns, all_encoders_):
		"""
		Transforms a pandas dataframe's categorical columns into pseudo-ordinal numerical columns based on existing mapping
		:param dframe: a pandas dataframe
		:param columns: list of column names to be transformed
		:param all_encoders_: same length list of sklearn encoders, each mapping categorical feature values to numbers
		:return: transformed numerical dataframe
		"""
		for idx, column in enumerate(columns):
			dframe.loc[:, column] = all_encoders_[idx].transform(dframe.loc[:, column].values)
		return dframe


	@staticmethod
	def n_gram(data, headers, cat_labels, num_labels):
		"""
		Turns unigram feature list into list of five-skipgram features by adding features of adjacent tokens

		:param data: List of observations, each an ordered list of feature values
		:param headers: List of all feature names in the data
		:param cat_labels: List of categorical features to be used in model
		:param num_labels: List of numerical features to be used in the model
		:return: Modified data, headers and label lists including adjacent token properties
		"""
		n_grammed = []

		data = [data[-2], data[-1]] + data + [data[0], data[1]]

		for i in range(2,len(data)-2):
			n_grammed.append(data[i-2]+data[i-1]+data[i]+data[i+1]+data[i+2])

		n_grammed_headers = [header + "_min2" for header in headers] + [header + "_min1" for header in headers] + headers + [header + "_pls1" for header in headers] + [header + "_pls2" for header in headers]
		n_grammed_cat_labels = [lab + "_min2" for lab in cat_labels] + [lab + "_min1" for lab in cat_labels] + cat_labels + [lab + "_pls1" for lab in cat_labels] + [lab + "_pls2" for lab in cat_labels]
		n_grammed_num_labels = [lab + "_min2" for lab in num_labels] + [lab + "_min1" for lab in num_labels] + num_labels + [lab + "_pls1" for lab in num_labels] + [lab + "_pls2" for lab in num_labels]

		return n_grammed, n_grammed_headers, n_grammed_cat_labels, n_grammed_num_labels


if __name__ == "__main__":

	p = ArgumentParser()
	p.add_argument("--mode",choices=["train","test","train-test","optimize-train-test"],default="train-test")
	p.add_argument("--train_list",default="silver")
	p.add_argument("--format",default="conll")
	p.add_argument("--infile",default=None)
	opts = p.parse_args()

	if opts.format == "sgml":
		train = list_files(opts.train_list)
		train = [f for f in train if "ap." not in f.lower()]
	else:
		ud_coptic = "C:\\Uni\\Coptic\\git\\UD_Coptic\\"
		files = ["cop_scriptorium-ud-dev.conllu","cop_scriptorium-ud-train.conllu","cop_scriptorium-ud-test.conllu"]
		train = [ud_coptic + f for f in files]

	# Predict sentence splits
	s = BGSentencer()

	if "train" in opts.mode:
		s.train(train,format=opts.format)
	else:
		if opts.infile is not None:
			preds = s.predict(opts.infile)
			sgml = open(opts.infile).read().strip()
			output = []
			counter = 0
			for line in sgml.split("\n"):
				if " norm_group=" in line:
					if preds[counter] == 1:
						if counter > 0:
							output.append("</translation>")
						output.append('<translation translation="...">')
					counter += 1
				elif '<chapter' in line:
					preds[counter]=1  # Ensure next bg is a split
				elif "</meta>" in line:
					output.append("</translation>")
				output.append(line)
			if "</meta>" not in sgml:
				output.append("</translation>")

			print("\n".join(output) + "\n")
		else:
			pred = s.predict("..\\eval\\unreleased\\BritMusOriental6783_27a_30a.tt",eval_gold=True)

# sentencer.py --mode test --infile=pistis.sophia_book_1_part2.tt --format=sgml