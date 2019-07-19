import sys, io, re, os
from glob import glob
from argparse import ArgumentParser
from sklearn.metrics import f1_score, precision_score, recall_score
from utils.eval_utils import list_files

PY3 = sys.version_info[0] == 3

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
plain_dir = script_dir + "plain" + os.sep
err_dir = script_dir + "errors" + os.sep

lex = script_dir + ".." + os.sep + "data" + os.sep + "copt_lemma_lex_cplx_2.5.tab"
frq = script_dir + ".." + os.sep + "data" + os.sep + "cop_freqs.tab"
conf = script_dir + ".." + os.sep + "data" + os.sep + "test.conf"
ambig = script_dir + ".." + os.sep + "data" + os.sep + "ambig.tab"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

from stacked_tokenizer import StackedTokenizer

IGNORE = [
	"",  #	 empty string
	"~",  # U+007E  TILDE
	"`",  # U+0060  GRAVE ACCENT
	"\n",  #	NEWLINE
	"̈",  # U+0308  COMBINING DIAERESIS
	"̄",  # U+0304  COMBINING MACRON
	"̀",  # U+0300  COMBINING GRAVE ACCENT
	"̣",  # U+0323  COMBINING DOT BELOW
	"̅",  # U+0305  COMBINING OVERLINE
	"̂",  # U+0302  COMBINING CIRCUMFLEX ACCENT
	"︤",  # U+FE24  COMBINING MACRON LEFT HALF
	"︥",  # U+FE25  COMBINING MACRON RIGHT HALF
	"︦",  # U+FE26  COMBINING CONJOINING MACRON
	"̇",  # U+0307  COMBINING DOT ABOVE
	"᷍",  # U+1DCD  COMBINING DOUBLE CIRCUMFLEX ABOVE
	"⳿",  # U+2CFF  COPTIC MORPHOLOGICAL DIVIDER
]
GOLD_TOKEN_SEPARATOR = "_"
ORIG_TOKEN_SEPARATOR = " "


# I/O and preprocessing -----------------------------------------------------------------------------------------------
def read_and_combine_files(file_list):
	"""Given a list of file paths, strip and add a newline character to the contents of each and concatenate them all
	together into a single string.
	:param file_list: a list of file paths
	:return: string contents of all files
	"""
	contents = ""
	for f in file_list:
		contents += io.open(f, encoding="utf8").read().strip() + "\n"
	return contents


def remove_chars(text, ignore_list):
	for c in ignore_list:
		text = text.replace(c, "")
	return text


def check_identical_text(gold, pred):
	"""For each character in gold, ensure that the corresponding character is identical in pred. Also check that lengths
	are identical. Characters in IGNORE + [ORIG_TOKEN_SEPARATOR, GOLD_TOKEN_SEPARATOR] are ignored.

	:param gold: The entire gold text string, with GOLD_TOKEN_SEPARATOR separating tokens
	:param pred: The entire pred text string
	"""
	counter = -1

	# ensure same length
	gold = remove_chars(gold, IGNORE + [ORIG_TOKEN_SEPARATOR, GOLD_TOKEN_SEPARATOR])
	pred = remove_chars(pred, IGNORE + [ORIG_TOKEN_SEPARATOR, GOLD_TOKEN_SEPARATOR])
	if len(gold) != len(pred):
		raise Exception("gold and pred have different lengths: len(gold)={}, len(pred)={}".format(len(gold), len(pred)))

	# ensure identical letters
	for i, gold_c in enumerate(gold):
		if gold_c == GOLD_TOKEN_SEPARATOR:
			continue
		else:
			counter += 1

		pred_c = pred[counter]

		if gold_c != pred_c:
			gold_start = max(i-15, 0)
			pred_start = max(counter-15, 0)
			raise Exception("non matching char at " + str(i) + ":\n"
							+ str(list(gold[gold_start:i+1])) + "\n"
							+ str(list(pred[pred_start:counter+1])))


def prepare_gold_text(gold_list):
	text = read_and_combine_files(gold_list)
	lines = text.split("\n")
	gold = []
	for line in lines:
		if "orig_group=" in line:
			grp = re.search('orig_group="([^"]*)"',line).group(1).strip()
			gold.append(grp.strip())
	return GOLD_TOKEN_SEPARATOR.join(gold)


def prepare_orig_lines(orig_list):
	text = read_and_combine_files(orig_list)
	text = clean(text)

	eval_orig_lines = []
	for line in text.strip().split("\n"):
		line = line.strip()
		if len(line) == 0:
			continue
		if line.endswith("‐"):
			line = line[:-1]
		else:
			line += " "
		eval_orig_lines.append(line)

	return eval_orig_lines


# No longer used
def test_train_split(gold, pred, train_proportion=0.8):
	split = int(len(gold) * train_proportion)
	split = gold.index(GOLD_TOKEN_SEPARATOR, split) + 1
	assert split != 0

	gold_train, gold_test = gold[:split], gold[split:]

	pred_i = 0
	for i, gold_c in enumerate(gold_train):
		if gold_c not in IGNORE + [ORIG_TOKEN_SEPARATOR, GOLD_TOKEN_SEPARATOR]:
			while pred[pred_i] != gold_c:
				pred_i += 1
	while pred[pred_i - 1] != ORIG_TOKEN_SEPARATOR:
		pred_i += 1

	pred_train, pred_test = pred[:pred_i], pred[pred_i:]

	assert (len(remove_chars(gold_train, IGNORE + [ORIG_TOKEN_SEPARATOR, GOLD_TOKEN_SEPARATOR]))
			== len(remove_chars(pred_train, IGNORE + [ORIG_TOKEN_SEPARATOR, GOLD_TOKEN_SEPARATOR])))
	return gold_train, pred_train, gold_test, pred_test


def clean(text):
	"""Cleans text by: (1) removing obviously non-Coptic text; (2) turning sequences of >=1 newline into a single
	newline; (3) turning sequences of >=1 space into a single space; (4) spacing out ., ·, and :
	:param text: A string of Coptic text
	:return: Cleaned Coptic text
	"""
	text = text.replace(".", " .").replace("·", " ·").replace(":", " : ")
	uncoptic1 = r'[A-Za-z0-9|]' # Latin or numbers, pipe
	uncoptic2 = r'\[F[^]]+\]'   # Square brackets if they start with F
	uncoptic3 = r'\([^\)]+\)'   # Anything in round brackets
	uncoptic = "("+"|".join([uncoptic1, uncoptic2, uncoptic3])+")"

	#text = re.sub(r'.*ⲦⲘⲀⲢⲦⲨⲢⲒⲀ','ⲦⲘⲀⲢⲦⲨⲢⲒⲀ',text,flags=re.MULTILINE|re.DOTALL)
	text = re.sub(uncoptic, '', text)
	text = re.sub(r"\n+", r"\n", text)
	text = re.sub(r" +", r" ", text)

	return text

# binding --------------------------------------------------------------------------------------------------------------
def bind_naive(test_orig_lines, gold):
	txt = "".join(test_orig_lines)
	check_identical_text(gold, txt)
	naive = txt.replace(ORIG_TOKEN_SEPARATOR, GOLD_TOKEN_SEPARATOR)

	scores, errs = binding_score(gold, naive)
	return scores


def bind_with_stacked_tokenizer(test_orig_lines, gold):
	stk = StackedTokenizer(no_morphs=True, model="test", pipes=True, detok=2, tokenized=True)
	stk.load_ambig(ambig_table=ambig)

	bound = stk.analyze("\n".join(test_orig_lines)).replace("|", "").replace('\n', '').strip()

	scores, errs = binding_score(gold,bound)
	with io.open(err_dir + "errs_binding_stacked.tab", 'w', encoding="utf8") as f:
		f.write("\n".join(errs) + "\n")

	return scores


def bind_with_logistic(test_orig_lines, test_gold, train_orig_lines, train_gold, opts):
	test_orig = "".join(test_orig_lines)
	train_orig = "".join(train_orig_lines)

	check_identical_text(test_orig, test_gold)
	check_identical_text(train_orig, train_gold)

	from binding.logistic import LogisticBindingModel
	m = LogisticBindingModel(
		ignore_chars=IGNORE,
		gold_token_separator=GOLD_TOKEN_SEPARATOR,
		orig_token_separator=ORIG_TOKEN_SEPARATOR,
		binding_freq_file_path=opts.detok_table,
		pos_file_path=opts.pos_table,
		group_freq_file_path=opts.group_freq_table,
	)
	m.train(train_gold, train_orig)
	pred = m.predict(test_orig)
	scores, errs = binding_score(test_gold, pred)

	with io.open(err_dir + "errs_binding_logistic.tab", 'w', encoding="utf8") as f:
		f.write("\n".join(errs) + "\n")

	return scores


def bind_with_xgboost(test_orig_lines, test_gold, train_orig_lines, train_gold, opts, **kwargs):
	test_orig = "".join(test_orig_lines)
	train_orig = "".join(train_orig_lines)

	check_identical_text(test_orig, test_gold)
	check_identical_text(train_orig, train_gold)

	from binding.xgboost import XGBoostBindingModel

	m = XGBoostBindingModel(
		ignore_chars=IGNORE,
		gold_token_separator=GOLD_TOKEN_SEPARATOR,
		orig_token_separator=ORIG_TOKEN_SEPARATOR,
		binding_freq_file_path=opts.detok_table,
		pos_file_path=opts.pos_table,
		group_freq_file_path=opts.group_freq_table,
		**kwargs
	)
	m.train(train_gold, train_orig)
	pred = m.predict(test_orig)
	scores, errs = binding_score(test_gold, pred)

	with io.open(err_dir + "errs_binding_xgboost.tab", 'w', encoding="utf8") as f:
		f.write("\n".join(errs) + "\n")

	return scores


def bind_with_lstm(test_orig_lines, gold, opts):
	txt = "".join(test_orig_lines)
	check_identical_text(gold, txt)

	from binding.lstm import LSTMBindingModel
	m = LSTMBindingModel(
		gold_token_separator=GOLD_TOKEN_SEPARATOR,
		pred_token_separator=ORIG_TOKEN_SEPARATOR
	)
	g_train, p_train, g_test, p_test = test_train_split(gold, txt)
	m.train(g_train)
	pred = m.predict(p_test)

	scores, errs = binding_score(g_test, pred)

	with io.open(err_dir + "errs_binding_logistic.tab", 'w', encoding="utf8") as f:
		f.write("\n".join(errs) + "\n")

	return scores


# evaluation -----------------------------------------------------------------------------------------------------------
def print_scores(scores, model_name):
	print("%s binding scores:" % model_name)
	print("Precision: %s" % scores["precision"])
	print("Recall:    %s" % scores["recall"])
	print("F1:        %s" % scores["f1"])
	print()


def binarize(text):
	"""Turn a text with _ separating bound groups into array of 0 (no split after character) or 1 (split after
	this character)

	Input: auO_prOme_...
	Output: [0,0,1,0,0,0,0,1,...]
	"""
	output = []

	for c in text:
		if c in IGNORE:
			continue
		if c == GOLD_TOKEN_SEPARATOR and len(output) > 0:
			output[-1] = 1
		else:
			output.append(0)
	return output


def binding_score(gold, pred):
	"""Calculate precision, recall, and f1.
	:param gold: Gold tokens separated by GOLD_TOKEN_SEPARATOR
	:param pred: Predicted tokens separated by GOLD_TOKEN_SEPARATOR
	:return: dict with keys "precision", "recall", "f1"
	"""
	bin_gold = binarize(gold)
	bin_pred = binarize(pred)

	gold_reached = 0
	pred_reached = 0
	gold_groups = gold.split(GOLD_TOKEN_SEPARATOR)
	pred_groups = pred.split(GOLD_TOKEN_SEPARATOR)
	errs = []
	for i, c in enumerate(range(len(bin_gold))):
		if bin_gold[i] == 1:
			gold_reached +=1
		if bin_pred[i] == 1:
			pred_reached +=1
		if bin_gold[i] != bin_pred[i]:
			gold_start = gold_end = gold_reached + 1
			pred_start = pred_end = pred_reached + 1
			if gold_reached > 0:
				pass
				gold_start = gold_reached-1
			if pred_reached > 0:
				pass
				pred_start = pred_reached -1
			if gold_reached < len(gold_groups)-1:
				gold_end = gold_reached +2
			if pred_reached < len(pred_groups) -1:
				pred_end = pred_reached +2
			errs.append("_".join(gold_groups[gold_start:gold_end]) + "\t" + "_".join(pred_groups[pred_start:pred_end]))

	scores = {
		"f1": f1_score(bin_gold,bin_pred),
		"precision": precision_score(bin_gold,bin_pred),
		"recall": recall_score(bin_gold,bin_pred)
	}

	return scores, errs


def run_eval(
		test_gold_list,
		test_orig_list,
		train_gold_list,
		train_orig_list,
		dev_gold_list,
		dev_orig_list,
		opts
):
	strategy = opts.strategy

	test_gold = prepare_gold_text(test_gold_list)
	print(test_orig_list)
	test_orig_lines = prepare_orig_lines(test_orig_list)

	train_gold = prepare_gold_text(train_gold_list)
	train_orig_lines = prepare_orig_lines(train_orig_list)

	dev_gold = prepare_gold_text(dev_gold_list)
	dev_orig_lines = prepare_orig_lines(dev_orig_list)

	if strategy == 'naive':
		baseline_scores = bind_naive(test_orig_lines, test_gold)
		print_scores(baseline_scores, 'Baseline')
		return baseline_scores
	elif strategy == 'stacked':
		st_scores = bind_with_stacked_tokenizer(test_orig_lines, test_gold)
		print_scores(st_scores, 'Stacked tokenizer')
		return st_scores
	elif strategy == 'logistic':
		logistic_scores = bind_with_logistic(
			test_orig_lines,
			test_gold,
			train_orig_lines,
			train_gold,
			opts
		)
		print_scores(logistic_scores, 'LogisticRegressionCV')
		return logistic_scores
	elif strategy == 'xgboost':
		xgboost_scores = bind_with_xgboost(
			test_orig_lines,
			test_gold,
			train_orig_lines,
			train_gold,
			opts
		)
		print_scores(xgboost_scores, 'XGBoost')
		return xgboost_scores
	elif strategy == 'xgboost-hyper':
		from hyperopt import hp, fmin, Trials, STATUS_OK, tpe
		from hyperopt.pyll import scope
		space = {
			'n_estimators': scope.int(hp.quniform('n_estimators', 100, 250, 10)),
			'max_depth': scope.int(hp.quniform('max_depth', 8, 35, 1)),
			'eta': scope.float(hp.quniform('eta', 0.01, 0.2, 0.01)),
			'gamma': scope.float(hp.quniform('gamma', 0.01, 0.2, 0.01)),
			'colsample_bytree': hp.choice('colsample_bytree', [0.6, 0.7, 0.8, 1.0]),
			#'colsample_bynode': hp.choice('colsample_bynode', [0.6, 0.7, 0.8, 1.0]),
			#'colsample_bylevel': hp.choice('colsample_bylevel', [0.6, 0.7, 0.8, 1.0]),
			'subsample': hp.choice('subsample', [0.6, 0.7, 0.8, 0.9, 1.0]),
		}

		def f(params):
			scores = bind_with_xgboost(
				dev_orig_lines,
				dev_gold,
				train_orig_lines,
				train_gold,
				opts,
				**params
			)
			return {'loss': -scores['f1'], 'status': STATUS_OK}

		trials = Trials()
		best = fmin(f, space, algo=tpe.suggest, max_evals=200, trials=trials)
		print("\nBest parameters:\n" + 30 * "=")
		print(best)
		xgboost_scores = bind_with_xgboost(
			test_orig_lines,
			test_gold,
			train_orig_lines,
			train_gold,
			opts,
			**best
		)
		print_scores(xgboost_scores, 'XGBoost hyper search')
		return xgboost_scores
	elif strategy == 'lstm':
		lstm_scores = bind_with_lstm(test_orig_lines, test_gold, opts)
		print_scores(lstm_scores, 'LSTM')
		return lstm_scores
	elif strategy == 'all':
		scores = bind_naive(test_orig_lines, test_gold)
		print_scores(scores, 'Baseline')
		scores = bind_with_logistic(
			test_orig_lines,
			test_gold,
			train_orig_lines,
			train_gold,
			opts
		)
		print_scores(scores, 'Logistic regression')
		scores = bind_with_xgboost(
			test_orig_lines,
			test_gold,
			train_orig_lines,
			train_gold,
			opts
		)
		print_scores(scores, 'XGBoost')
		#_ = bind_with_lstm(test_orig_lines, gold, opts)
		scores = bind_with_stacked_tokenizer(test_orig_lines, test_gold)
		print_scores(scores, 'Stacked tokenizer')
	else:
		raise Exception("Unknown strategy: '{}'.\nMust be one of 'naive', 'stacked', 'logistic', 'xgboost', 'xgboost-hyper', 'lstm', 'all'."
						.format(strategy))


# command line interface -----------------------------------------------------------------------------------------------
def resolve_file_lists(file_list, synthetic=False):
	gold = list_files(file_list)
	orig = list_files(file_list,mode="plain")

	file_dir = "plain"
	gold_dir = "unreleased"

	if synthetic:
		gold.append(script_dir + gold_dir + os.sep + 'aug_bind_uddev_gold.tt')
		orig.append(script_dir + file_dir + os.sep + 'aug_bind_uddev.txt')
		gold.append(script_dir + gold_dir + os.sep + 'aug_bind_udtrain_gold.tt')
		orig.append(script_dir + file_dir + os.sep + 'aug_bind_udtrain.txt')
	return gold, orig



def main():
	p = ArgumentParser()
	p.add_argument(
		"strategy",
		default="all",
		help="binding strategy: one of 'naive', 'stacked', 'logistic', 'xgboost', 'xgboost-hyper', 'lstm', 'all'",
		nargs='?'
	)
	p.add_argument(
		"--train_list",
		default="victor",
		help="file with one file name per line of TT SGML training files or alias of train set, e.g. 'silver'; all files not in test if not supplied"
	)

	p.add_argument(
		"--test_list",
		default="cyrus",
		help="file with one file name per line of TT SGML training files or alias of train set, e.g. 'silver'; all files not in test if not supplied"
	)
	p.add_argument(
		"--dev_list",
		default="onno",
		help="file with one file name per line of TT SGML training files or alias of train set, e.g. 'silver'; all files not in dev if not supplied"
	)
	p.add_argument(
		"--detok_table",
		default=os.sep.join(['..', 'data', 'detok.tab']),
		help="A TSV file containing bound groups and their binding frequencies"
	)
	p.add_argument(
		"--pos_table",
		default="copt_lemma_lex_cplx_2.8_cdo.tab", #TODO: change this
		help="A TSV file containing POS information"
	)
	p.add_argument(
		"--group_freq_table",
		default=os.sep.join(['..', 'data', 'annis_silver_orig_group_freqs_2019_07.tab']), #TODO: change this
		help="A TSV file containing orig group freq information in silver data"
	)
	p.add_argument("--synthetic",action="store_true",help="User synthetic training data")


	opts = p.parse_args()

	test_gold_list, test_orig_list = resolve_file_lists(
		opts.test_list
	)

	train_gold_list, train_orig_list = resolve_file_lists(
		opts.train_list,
		synthetic=opts.synthetic
	)

	dev_gold_list, dev_orig_list = resolve_file_lists(
		opts.dev_list
	)

	run_eval(
		test_gold_list,
		test_orig_list,
		train_gold_list,
		train_orig_list,
		dev_gold_list,
		dev_orig_list,
		opts
	)


if __name__ == "__main__":
	main()
