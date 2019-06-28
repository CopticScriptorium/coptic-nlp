import sys, io, re, os
from glob import glob
from argparse import ArgumentParser
from utils.f_score_segs import main as f_score
from utils.eval_utils import list_files
from collections import defaultdict
from six import iterkeys, iteritems

PY3 = sys.version_info[0] == 3

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
err_dir = script_dir + "errors" + os.sep

lex = script_dir + ".." + os.sep + "data" + os.sep + "copt_lemma_lex_cplx_2.5.tab"
lex = script_dir + "copt_lemma_lex_cplx_2.8_cdo.tab"
data_dir = script_dir + ".." + os.sep + "data" + os.sep
frq = data_dir + "cop_freqs.tab"
conf = data_dir + "test.conf"
ambig = data_dir + "ambig.tab"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

from tokenize_rf import RFTokenizer
from stacked_tokenizer import StackedTokenizer


def tsv2dict(filename,as_string=False):
	"""Read a tsv file and return dict of col0 -> col1"""
	if as_string:
		rows = filename.strip().split("\n")
	else:
		rows = io.open(filename,encoding="utf8").read().replace("\r","").strip().split("\n")
	tuples = [row.split("\t") for row in rows if "\t" in row]
	d = dict((t[0],t[1]) for t in tuples)
	return d


def tt2seg_table(tt_string,group_attr="norm_group",unit_attr="norm"):

	group = ""
	output = ""
	units = []
	pairs = []
	unit = ""
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


def run_eval(train_list, test_list, retrain_rf=False, method="stacked", importances=False,optimize=False):

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

	# Make lookup seg table
	lookup = {}
	ambig_entries = defaultdict(set)
	old_segs = tsv2dict(data_dir + "segmentation_table_2.7.tab")
	seg_counts = defaultdict(lambda : defaultdict(int))
	# Get UD gold data to rule out illegal deterministic segmentations
	ud = list_files("ud_train")
	ud += list_files("ud_dev")
	ud_dev_train = ""
	for file_ in ud:
		tt_sgml = io.open(file_,encoding="utf8").read()
		ud_dev_train += tt2seg_table(tt_sgml)
	ud_dict = tsv2dict(ud_dev_train,as_string=True)

	for line in train.strip().split("\n"):
		bg, analysis = line.split("\t")
		seg_counts[bg][analysis] += 1
	for bg in seg_counts:
		for ana in seg_counts[bg]:
			if len(seg_counts[bg]) == 1:
				if seg_counts[bg][ana] > 0: #and bg not in old_segs:  # 1:  # use 1 to filter out hapax cases
					if bg in ud_dict:  # Prohibit storing analysis that contradicts UD gold data
						if ud_dict[bg] == ana:
							lookup[bg] = ana
					else:
						lookup[bg] = ana
			else:
				ambig_entries[bg].add(ana)
	for bg in old_segs:
		lookup[bg] = old_segs[bg]
	temp = []
	for bg in ambig_entries:
		alternatives = sorted(list(ambig_entries[bg]),reverse=True,key=lambda x: seg_counts[bg][x])
		temp.append(bg + "\t" + "\t".join(alternatives))
	ambig_entries = temp
	with io.open(data_dir + "segmentation_table.tab",'w', encoding="utf8",newline="\n") as f:
		f.write("\n".join([k+"\t"+v for k,v in iteritems(lookup)])+"\n")
	with io.open(data_dir + "ambig.tab",'w', encoding="utf8",newline="\n") as f:
		f.write("\n".join(ambig_entries)+"\n")

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
		rf.train(script_dir + "_tmp_train.tab",lexicon_file=lex,freq_file=frq,test_prop=0,dump_model=True,output_errors=True,conf=conf,
				 output_importances=importances, cross_val_test=optimize)
		preds = rf.rf_tokenize(test_input)
		f_score(script_dir + "_tmp_test.tab","\n".join(preds),preds_as_string=True,ignore_diff_len=True)

	if method == "stacked":
		stk = StackedTokenizer(no_morphs=True,model="test",pipes=True,ambig=ambig)

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


	# Analyze errors
	errs = defaultdict(int)
	for i, pred in enumerate(preds):
		gold = golds[i].split("\t")[1]
		if pred != gold:
			errs[gold + "\t"+ pred] += 1

	err_sources = {}
	seg_table = tsv2dict(script_dir +".." + os.sep + "data" +os.sep+"segmentation_table.tab")
	ambig_table = tsv2dict(script_dir +".." + os.sep + "data" +os.sep+"ambig.tab")
	for_fs = set([])
	for key in errs:
		bg = key.split("\t")[0].replace("|","")
		if bg in ambig_table:
			err_sources[bg] = "ambig"
		elif bg in seg_table:
			err_sources[bg] = "lookup"
		else:
			for_fs.add(bg)
	if len(for_fs) > 0:
		try:
			from .tokenize_fs import fs_tokenize
		except:
			from tokenize_fs import fs_tokenize
		tokenizations_fs = fs_tokenize(list(for_fs))
		for tk in tokenizations_fs:
			if "|" in tk:
				err_sources[tk.replace("|","")] = "fs"

	with io.open(err_dir + "errs_tokenization.tab",'w',encoding="utf8") as f:
		for key in sorted(iterkeys(errs),key=lambda x:errs[x],reverse=True):
			bg = key.split("\t")[0].replace("|","")
			err_src = err_sources[bg] if bg in err_sources else "rf"
			f.write(key + "\t" + str(errs[key]) + "\t" + err_src + "\n")

	return scores


if __name__ == "__main__":
	p = ArgumentParser()
	p.add_argument("--train_list",default=None,help="file with one file name per line of TT SGML training files; all files not in test if not supplied")
	p.add_argument("--test_list",default="test_list.tab",help="file with one file name per line of TT SGML test files")
	p.add_argument("--file_dir",default="tt",help="directory with TT SGML files")
	p.add_argument("--method",default="stacked",choices=["stacked","lookup","finitestate","rf"],help="tokenizer to use")
	p.add_argument("-r","--retrain",action="store_true",help="whether to retrain RF tokenizer")
	p.add_argument("-i","--importances",action="store_true",help="whether to output feature importances when retraining RF tokenizer")
	p.add_argument("-o","--optimize",action="store_true",help="whether to run hyperparameter optimization when retraining RF tokenizer")

	opts = p.parse_args()

	if os.path.isfile(opts.test_list):
		test_list = io.open(opts.test_list,encoding="utf8").read().strip().split("\n")
		test_list = [script_dir + opts.file_dir + os.sep + f for f in test_list]
	else:
		test_list = list_files(opts.test_list)
		test_list = [os.path.abspath(f) for f in test_list]

	if opts.train_list is not None:
		if os.path.isfile(opts.train_list):
			train_list = io.open(opts.train_list,encoding="utf8").read().strip().split("\n")
			train_list = [script_dir + opts.file_dir + os.sep + f for f in train_list]
		else:
			train_list = list_files(opts.train_list)
	else:
		train_list = glob(opts.file_dir + os.sep + "*.tt")
		train_list = [os.path.abspath(f) for f in train_list]
		train_list = [f for f in train_list if f not in test_list]

	if not os.path.isfile("test.sm" + str(sys.version_info[0])) and not opts.retrain and opts.method !="finitestate":
		sys.stderr.write("o Could not find tokenizer model test.sm3\n")
		sys.stderr.write("o Switching on option --retrain\n")
		retrain = True
	else:
		retrain = opts.retrain

	run_eval(train_list,test_list,retrain_rf=retrain,method=opts.method,importances=opts.importances,optimize=opts.optimize)
