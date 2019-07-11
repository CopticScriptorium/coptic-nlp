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
TOKEN_SEPARATOR = "_"

# I/O and preprocessing -----------------------------------------------------------------------------------------------
def read_file_list(file_list):
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
	are identical. Characters in IGNORE + [" ", TOKEN_SEPARATOR] are ignored.

	:param gold: The entire gold text string, with TOKEN_SEPARATOR separating tokens
	:param pred: The entire pred text string
	"""
	counter = -1

	# ensure same length
	gold = remove_chars(gold, IGNORE + [" ", TOKEN_SEPARATOR])
	pred = remove_chars(pred, IGNORE + [" ", TOKEN_SEPARATOR])
	if len(gold) != len(pred):
		raise Exception("gold and pred have different lengths: len(gold)={}, len(pred)={}".format(len(gold), len(pred)))

	# ensure identical letters
	for i, gold_c in enumerate(gold):
		if gold_c == TOKEN_SEPARATOR:
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


def test_train_split(gold, pred, train_proportion=0.8):
	split = int(len(gold) * train_proportion)
	split = gold.index(TOKEN_SEPARATOR, split) + 1
	assert split != 0

	gold_train, gold_test = gold[:split], gold[split:]

	pred_i = 0
	for i, gold_c in enumerate(gold_train):
		if gold_c not in IGNORE + [" ", TOKEN_SEPARATOR]:
			while pred[pred_i] != gold_c:
				pred_i += 1
	while pred[pred_i - 1] != " ":
		pred_i += 1

	pred_train, pred_test = pred[:pred_i], pred[pred_i:]

	assert (len(remove_chars(gold_train, IGNORE + [" ", TOKEN_SEPARATOR]))
			== len(remove_chars(pred_train, IGNORE + [" ", TOKEN_SEPARATOR])))
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
def bind_naive(lines_to_process, gold):
	txt = "".join(lines_to_process)
	check_identical_text(gold, txt)
	naive = txt.replace(" ", TOKEN_SEPARATOR)

	scores, errs = binding_score(gold, naive)
	print("Baseline scores:")
	print("Precision: %s" % scores["precision"])
	print("Recall:    %s" % scores["recall"])
	print("F1:	%s" % scores["f1"])
	return scores

def bind_with_stacked_tokenizer(lines_to_process, gold):
	stk = StackedTokenizer(no_morphs=True, model="test", pipes=True, detok=2, tokenized=True)
	stk.load_ambig(ambig_table=ambig)

	bound = stk.analyze("\n".join(lines_to_process)).replace("|", "").replace('\n', '').strip()

	scores, errs = binding_score(gold,bound)
	print("Stacked binding scores:")
	print("Precision: %s" % scores["precision"])
	print("Recall:    %s" % scores["recall"])
	print("F1:	%s" % scores["f1"])

	with io.open(err_dir + "errs_binding_stacked.tab", 'w', encoding="utf8") as f:
		f.write("\n".join(errs) + "\n")

	return scores


def bind_with_logistic(lines_to_process, gold):
	txt = "".join(lines_to_process)
	check_identical_text(gold, txt)

	from binding.logistic import LogisticBindingModel
	m = LogisticBindingModel(gold_token_separator=TOKEN_SEPARATOR, pred_token_separator=" ")
	g_train, p_train, g_test, p_test = test_train_split(gold, txt)
	m.train(g_train)
	pred = m.predict(p_test)

	scores, errs = binding_score(g_test, pred)
	print("Logistic regression binding scores:")
	print("Precision: %s" % scores["precision"])
	print("Recall:    %s" % scores["recall"])
	print("F1:	      %s" % scores["f1"])

	with io.open(err_dir + "errs_binding_logistic.tab", 'w', encoding="utf8") as f:
		f.write("\n".join(errs) + "\n")

	return scores


def bind_with_lstm(lines_to_process, gold):
	txt = "".join(lines_to_process)
	check_identical_text(gold, txt)

	from binding.lstm import LSTMBindingModel
	m = LogisticBindingModel(gold_token_separator=TOKEN_SEPARATOR, pred_token_separator=" ")
	g_train, p_train, g_test, p_test = test_train_split(gold, txt)
	m.train(g_train)
	pred = m.predict(p_test)

	scores, errs = binding_score(g_test, pred)
	print("Logistic regression binding scores:")
	print("Precision: %s" % scores["precision"])
	print("Recall:    %s" % scores["recall"])
	print("F1:	      %s" % scores["f1"])

	with io.open(err_dir + "errs_binding_logistic.tab", 'w', encoding="utf8") as f:
		f.write("\n".join(errs) + "\n")

	return scores



# evaluation -----------------------------------------------------------------------------------------------------------
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
		if c == TOKEN_SEPARATOR and len(output) > 0:
			output[-1] = 1
		else:
			output.append(0)
	return output


def binding_score(gold, pred):
	"""Calculate precision, recall, and f1.
	:param gold: Gold tokens separated by TOKEN_SEPARATOR
	:param pred: Predicted tokens separated by TOKEN_SEPARATOR
	:return: dict with keys "precision", "recall", "f1"
	"""
	bin_gold = binarize(gold)
	bin_pred = binarize(pred)

	gold_reached = 0
	pred_reached = 0
	gold_groups = gold.split(TOKEN_SEPARATOR)
	pred_groups = pred.split(TOKEN_SEPARATOR)
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
			errs.append(" ".join(gold_groups[gold_start:gold_end]) + "\t" + " ".join(pred_groups[pred_start:pred_end]))

	scores = {
		"f1": f1_score(bin_gold,bin_pred),
		"precision": precision_score(bin_gold,bin_pred),
		"recall": recall_score(bin_gold,bin_pred)
	}

	return scores, errs


def run_eval(gold_list, test_list, strategy):
	gold = read_file_list(gold_list)
	test = read_file_list(test_list)
	test = clean(test)

	lines_to_process = []
	for line in test.strip().split("\n"):
		line = line.strip()
		if len(line) == 0:
			continue
		if line.endswith("‐"):
			line = line[:-1]
		else:
			line += " "
		lines_to_process.append(line)

	# Get gold data
	lines = gold.split("\n")
	gold = []
	for line in lines:
		if "orig_group=" in line:
			grp = re.search('orig_group="([^"]*)"',line).group(1).strip()
			gold.append(grp.strip())
	gold = TOKEN_SEPARATOR.join(gold)

	if strategy == 'naive':
		baseline_scores = bind_naive(lines_to_process, gold)
		return baseline_scores
	elif strategy == 'stacked':
		st_scores = bind_with_stacked_tokenizer(lines_to_process, gold)
		return st_scores
	elif strategy == 'logistic':
		logistic_scores = bind_with_logistic(lines_to_process, gold)
		return logistic_scores
	elif strategy == 'lstm':
		lstm_scores = bind_with_lstm(lines_to_process, gold)
		return lstm_scores
	elif strategy == 'all':
		_ = bind_naive(lines_to_process, gold)
		_ = bind_with_logistic(lines_to_process, gold)
		_ = bind_with_lstm(lines_to_process, gold)
		st_scores = bind_with_stacked_tokenizer(lines_to_process, gold)
		return st_scores
	else:
		raise Exception("Unknown strategy: '{}'.\nMust be one of 'naive', 'stacked', 'logistic', 'lstm', 'all'."
						.format(strategy))


def main():
	p = ArgumentParser()
	p.add_argument("strategy",default="all",help="binding strategy: one of 'naive', 'stacked', 'logistic', 'lstm', 'all'", nargs='?')
	p.add_argument("--train_list",default="victor_tt",help="file with one file name per line of TT SGML training files or alias of train set, e.g. 'silver'; all files not in test if not supplied")
	p.add_argument("--test_list",default="victor_plain",help="file with one file name per line of plain text test files, or alias of test set, e.g. 'ud_test'")
	p.add_argument("--file_dir",default="plain",help="directory with plain text files")
	p.add_argument("--gold_dir",default="unreleased",help="directory with gold .tt files")

	opts = p.parse_args()

	train_list = opts.train_list
	test_list = opts.test_list
	if opts.test_list.startswith("onno"):
		test_list = "onno_plain"
		train_list = "onno"
	if opts.test_list.startswith("cyrus"):
		test_list = "cyrus_plain"
		train_list = "cyrus"

	if os.path.isfile(test_list):
		test_list = io.open(opts.test_list,encoding="utf8").read().strip().split("\n")
		test_list = [script_dir + opts.file_dir + os.sep + f for f in test_list]
	else:
		test_list = list_files(test_list)

	if train_list is not None:
		if os.path.isfile(train_list):
			train_list = io.open(train_list,encoding="utf8").read().strip().split("\n")
			train_list = [script_dir + opts.gold_dir + os.sep + f for f in train_list]
		else:
			train_list = list_files(train_list)
	else:
		train_list = glob(script_dir + opts.gold_dir + os.sep + "*.tt")
		train_list = [os.path.basename(f) for f in train_list if os.path.basename(f) not in test_list]
		train_list = [script_dir + opts.gold_dir + os.sep + f for f in train_list]

	scores = run_eval(train_list, test_list, opts.strategy)


if __name__ == "__main__":
	main()
