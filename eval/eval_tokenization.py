import sys, io, re, os
from glob import glob
from argparse import ArgumentParser
from utils.f_score_segs import main as f_score
from utils.eval_utils import list_files
from collections import defaultdict
from six import iterkeys

PY3 = sys.version_info[0] == 3

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
err_dir = script_dir + "errors" + os.sep

lex = script_dir + ".." + os.sep + "data" + os.sep + "copt_lemma_lex_cplx_2.5.tab"
frq = script_dir + ".." + os.sep + "data" + os.sep + "cop_freqs.tab"
conf = script_dir + ".." + os.sep + "data" + os.sep + "test.conf"
ambig = script_dir + ".." + os.sep + "data" + os.sep + "ambig.tab"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

from tokenize_rf import RFTokenizer
from stacked_tokenizer import StackedTokenizer


def tt2seg_table(tt_string,group_attr="norm_group",unit_attr="norm"):

	group = ""
	output = ""
	units = []
	pairs = []
	for line in tt_string.split("\n"):
		if " " + group_attr + "=" in line:  # new group
			group = re.search(" " + group_attr + '="([^"]+)"',line).group(1)
		if "</" + group_attr +">" in line:
			pairs.append((group,"|".join(units)))
			group = ""
			units = []
		if " " + unit_attr + "=" in line:  # new unit
			unit = re.search(" " + unit_attr + '="([^"]+)"',line).group(1)
			units.append(unit)

	for grp, segs in pairs:
		output += grp + "\t" + segs + "\n"

	return output


def run_eval(train_list, test_list, retrain_rf=False, method="stacked"):

	test = ""
	for file_ in test_list:
		tt_sgml = io.open(file_,encoding="utf8").read()
		test += tt2seg_table(tt_sgml)

	train = ""
	for file_ in train_list:
		tt_sgml = io.open(file_,encoding="utf8").read()
		train += tt2seg_table(tt_sgml)

	# Remove bug rows
	clean_test = []
	for line in test.strip().split("\n"):
		grp, seg = line.split("\t")
		if len(grp) == len(seg.replace("|","")):
			clean_test.append(line)
	test = "\n".join(clean_test)

	rf = RFTokenizer(model="test")  # Using temporary test model from eval dir
	if not PY3:
		train = unicode(train)

	with io.open(script_dir + "_tmp_train.tab",'w', encoding="utf8",newline="\n") as f:
		f.write(train)

	with io.open(script_dir + "_tmp_test.tab",'w', encoding="utf8",newline="\n") as f:
		f.write(test)

	test_input = ""
	for line in test.strip().split("\n"):
		test_input += line.split("\t")[0] + "\n"
	test_input = test_input.strip().split("\n")

	golds = test.split("\n")

	if retrain_rf:
		print("Retraining rf_tokenizer\n=============================")
		rf.train(script_dir + "_tmp_train.tab",lexicon_file=lex,freq_file=frq,test_prop=0,dump_model=True,output_errors=True,conf=conf)
		preds = rf.rf_tokenize(test_input)
		f_score(script_dir + "_tmp_test.tab","\n".join(preds),preds_as_string=True,ignore_diff_len=True)

	if method == "stacked":
		stk = StackedTokenizer(no_morphs=True,model="test",pipes=True)
		stk.load_ambig(ambig_table=ambig)

		preds = stk.analyze("_".join(test_input))
		preds = preds.split("_")
	elif method == "rf":
		preds = rf.rf_tokenize(test_input)
	elif method == "finitestate":
		from tokenize_fs import fs_tokenize
		preds = fs_tokenize(test_input)
	elif method == "lookup":
		from tokenize_lookup import lookup_tokenize
		preds = lookup_tokenize(test_input)

	scores = f_score(script_dir + "_tmp_test.tab","\n".join(preds),preds_as_string=True,ignore_diff_len=True,replace_diff_len=True)

	baseline = f_score(script_dir + "_tmp_test.tab","\n".join(test_input),preds_as_string=True,ignore_diff_len=True,replace_diff_len=True,silent=True)
	scores["baseline"] = baseline["acc"]

	errs = defaultdict(int)
	for i, pred in enumerate(preds):
		gold = golds[i].split("\t")[1]
		if pred != gold:
			errs[gold + "\t"+ pred] += 1

	with io.open(err_dir + "errs_tokenization.tab",'w',encoding="utf8") as f:
		for key in sorted(iterkeys(errs),reverse=True):
			f.write(key + "\t" + str(errs[key]) + "\n")

	return scores


if __name__ == "__main__":
	p = ArgumentParser()
	p.add_argument("--train_list",default=None,help="file with one file name per line of TT SGML training files; all files not in test if not supplied")
	p.add_argument("--test_list",default="test_list.tab",help="file with one file name per line of TT SGML test files")
	p.add_argument("--file_dir",default="tt",help="directory with TT SGML files")
	p.add_argument("--method",default="stacked",choices=["stacked","lookup","finitestate","rf"],help="directory with TT SGML files")
	p.add_argument("--retrain",action="store_true",help="whether to retrain RF tokenizer")

	opts = p.parse_args()

	if os.path.isfile(opts.test_list):
		test_list = io.open(opts.test_list,encoding="utf8").read().strip().split("\n")
		test_list = [script_dir + opts.file_dir + os.sep + f for f in test_list]
	else:
		test_list = list_files(opts.test_list)

	if opts.train_list is not None:
		if os.path.isfile(opts.train_list):
			train_list = io.open(opts.train_list,encoding="utf8").read().strip().split("\n")
			train_list = [script_dir + opts.file_dir + os.sep + f for f in train_list]
		else:
			train_list = list_files(opts.train_list)
	else:
		train_list = glob(opts.file_dir + os.sep + "*.tt")
		train_list = [os.path.basename(f) for f in train_list if os.path.basename(f) not in test_list]
		train_list = [script_dir + opts.file_dir + os.sep + f for f in train_list]

	if not os.path.isfile("test.sm" + str(sys.version_info[0])) and not opts.retrain and opts.method !="finitestate":
		sys.stderr.write("o Could not find tokenizer model test.sm3\n")
		sys.stderr.write("o Switching on option --retrain\n")
		retrain = True
	else:
		retrain = opts.retrain

	run_eval(train_list,test_list,retrain_rf=retrain,method=opts.method)
