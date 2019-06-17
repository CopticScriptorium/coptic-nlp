import sys, io, re, os
from glob import glob
from argparse import ArgumentParser
from utils.f_score_segs import main as f_score
from collections import defaultdict
from six import iterkeys
from tt import train_tt, tag_tt

PY3 = sys.version_info[0] == 3

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
err_dir = script_dir + "errors" + os.sep
lib = os.path.abspath(script_dir + os.sep + ".." + os.sep + "lib")
sys.path.append(lib)
from auto_norm import normalize
from utils.eval_utils import list_files

orig_chars = ["̈", "", "̄", "̀", "̣", "`", "̅", "̈", "̂", "︤", "︥", "︦", "⳿", "~", "\n", "[", "]", "̇", "᷍"]

def clean(text):
	if not text in ["[","]"]:
		for c in orig_chars:
			text = text.replace(c,"")
	return text

def tt2norm(tt_string,file_,orig_attr="orig_group",unit_attr="norm_group"):

	output = []
	wait = False
	for i,line in enumerate(tt_string.split("\n")):
		if " " + unit_attr + "=" in line:  # new group
			unit = re.search(" " + unit_attr + '="([^"]*)"',line).group(1).strip()
			if len(unit) == 0:
				sys.stderr.write("WARN: empty word on line " + str(i) + " in document " +os.path.basename(file_)+ "\n")
				wait = True
		if " " + orig_attr + "=" in line:  # new group
			orig = re.search(" " + orig_attr + '="([^"]*)"',line).group(1)
			if len(orig) == 0:
				sys.stderr.write("WARN: empty orig on line " + str(i) + " in document " +os.path.basename(file_) + "\n")
		if "</" + unit_attr + ">" in line:
			if wait:
				wait=False
				continue
			# flush
			try:
				if "\t" in orig or "\t" in unit:
					print("Error at " + str(i))
					sys.exit()
				output.append("\t".join([orig,unit]))
			except:
				print(file_,str(i))

	return "\n".join(output)+"\n"


def run_eval(train_list, test_list):

	test = ""
	for file_ in test_list:
		tt_sgml = io.open(file_,encoding="utf8").read()
		test += tt2norm(tt_sgml,file_)

	train = ""
	for file_ in train_list:
		tt_sgml = io.open(file_,encoding="utf8").read()
		train += tt2norm(tt_sgml,file_)

	if not PY3:
		train = unicode(train)

	with io.open(script_dir + "_tmp_norm_train.tab",'w', encoding="utf8") as f:
		f.write(train)


	test_origs = [line.split("\t")[0] for line in test.strip().split("\n")]
	test_norms = [line.split("\t")[1] for line in test.strip().split("\n")]

	test_origs = [clean(o) for o in test_origs]

	train_tab = script_dir + "_tmp_norm_train.tab"
	#train_tab = None

	normed = normalize("\n".join(test_origs).strip(),table_file=train_tab).strip().split("\n")

	errs = defaultdict(int)
	total = 0
	correct = 0
	trivial = 0
	ignore_single = True

	for i, auto in enumerate(normed):
		total += 1
		if auto != test_norms[i] and not (ignore_single and len(test_origs[i])==1):
			errs[test_origs[i] + "\t" + test_norms[i] + "\t"+ auto] += 1
		else:
			correct +=1
		if test_norms[i] == clean(test_origs[i]):
			trivial += 1

	bg_norm_acc = correct/float(total)
	trivial_prop = trivial/float(total)
	non_trivial_count = total-trivial
	non_trivial_acc = (correct-trivial)/float(total-trivial)

	print("Normalization accuracy (bound group): " + str(bg_norm_acc))
	print("Trivial proportion (bound group): " + str(trivial_prop))
	print("Non-trivial count: " + str(non_trivial_count) + "/" + str(total) + " (" + str(100*(total-trivial)/float(total)) + "%)")
	print("Accuracy on non-trivial (bound group): " + str(non_trivial_acc))

	with io.open(err_dir + "errs_norming.tab",'w',encoding="utf8") as f:
		for key in sorted(iterkeys(errs),key=lambda x:errs[x],reverse=True):
			f.write(key + "\t" + str(errs[key]) + "\n")

	return {"acc":bg_norm_acc, "baseline":trivial_prop, "non_trivial_count":non_trivial_count, "non_trivial_acc":non_trivial_acc}


if __name__ == "__main__":
	p = ArgumentParser()
	p.add_argument("--train_list",default=None,help="file with one file name per line of TT SGML training files or alias of train set, e.g. 'silver'; all files not in test if not supplied")
	p.add_argument("--test_list",default="test_list.tab",help="file with one file name per line of TT SGML test files, or alias of test set, e.g. 'ud_test'")
	p.add_argument("--file_dir",default="tt",help="directory with TT SGML files")

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

	run_eval(train_list,test_list)
