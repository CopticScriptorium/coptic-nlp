import sys, io, re, os
from glob import glob
from argparse import ArgumentParser
from utils.f_score_segs import main as f_score
from utils.eval_utils import list_files
from collections import defaultdict
from six import iterkeys
from tt import train_tt, tag_tt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

from marmot import train_marmot, tag_marmot
from stanford import train_stanford, tag_stanford

PY3 = sys.version_info[0] == 3

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
err_dir = script_dir + "errors" + os.sep


def tt2tagger(tt_string,file_,pos_attr="pos",unit_attr="norm",lemma_attr="lemma"):

	output = []
	wait = False
	for i,line in enumerate(tt_string.split("\n")):
		if " " + unit_attr + "=" in line:  # new group
			unit = re.search(" " + unit_attr + '="([^"]*)"',line).group(1).strip()
			if len(unit) == 0:
				sys.stderr.write("WARN: empty word on line " + str(i) + " in document " +os.path.basename(file_)+ "\n")
				wait = True
		if " " + pos_attr + "=" in line:  # new group
			p = re.search(" " + pos_attr + '="([^"]*)"',line).group(1)
			if len(p) == 0:
				sys.stderr.write("WARN: empty pos on line " + str(i) + " in document " +os.path.basename(file_) + "\n")
		if " " + lemma_attr + "=" in line:  # new group
			lemma = re.search(" " + lemma_attr + '="([^"]*)"',line).group(1)
			if len(lemma) == 0:
				sys.stderr.write("WARN: empty lemma on line " + str(i) + " in document " +os.path.basename(file_) + "\n")
		if "</" + unit_attr + ">" in line:
			if wait:
				wait=False
				continue
			# flush
			try:
				output.append("\t".join([unit,p,lemma]))
			except:
				print(file_,str(i))

	return "\n".join(output)+"\n"


def run_eval(train_list, test_list, tagger="tt", retrain=True):

	test = ""
	for file_ in test_list:
		tt_sgml = io.open(file_,encoding="utf8").read()
		test += tt2tagger(tt_sgml,file_)

	train = ""
	for file_ in train_list:
		tt_sgml = io.open(file_,encoding="utf8").read()
		train += tt2tagger(tt_sgml,file_)

	if not PY3:
		train = unicode(train)

	#with io.open("_tmp_train_tag.txt",'w',encoding="utf8") as f:
	#	f.write(train)

	if retrain:
		if tagger in ["marmot", "ensemble"]:
			train_marmot(train)
		if tagger in ["stanford","ensemble"]:
			train_stanford(train)
		if tagger in ["tt","ensemble"]:
			train_tt(train)

	to_tag = [line.split("\t")[0] for line in test.strip().split("\n")]
	golds = [line.split("\t") for line in test.strip().split("\n")]
	if tagger == "marmot":
		preds = tag_marmot("\n".join(to_tag)+"\n")
	elif tagger== "stanford":
		preds = tag_stanford("\n".join(to_tag)+"\n")
	elif tagger == "ensemble":
		marm = tag_marmot("\n".join(to_tag)+"\n")
		marm = [line.split("\t") for line in marm.replace("\r","").strip().split("\n")]
		stan = tag_stanford("\n".join(to_tag)+"\n")
		stan = [line.split("\t") for line in stan.replace("\r","").strip().split("\n")]
		tt = tag_tt("\n".join(to_tag)+"\n")
		tt = [line.split("\t") for line in tt.replace("\r","").strip().split("\n")]
		preds = marm
		for i in range(len(tt)):
			if tt[i][1] != preds[i][1] and tt[i][1] == stan[i][1]:
				preds[i][1] = tt[i][1]
	else:
		preds = tag_tt("\n".join(to_tag)+"\n")

	if tagger != "ensemble":
		preds = [line.split("\t") for line in preds.replace("\r","").strip().split("\n")]

	errs = defaultdict(int)
	total = 0
	correct = 0
	baseline = 0
	for i, line in enumerate(preds):
		total += 1
		tok,pos = line[0],line[1]
		gold = golds[i][1]
		if pos != gold:
			errs[tok + "\t" + gold + "\t"+ pos] += 1
			#errs[tok + "\t" + gold + "\t"+ pos + "\t" + preds[i-1][0] ] += 1  # Replace this with above for err context
		else:
			correct +=1
		if gold =="PREP": # Most frequent tag
			baseline +=1

	print("Tagging accuracy: " + str(correct/float(total)))

	with io.open(err_dir + "errs_tagging.tab",'w',encoding="utf8") as f:
		for key in sorted(iterkeys(errs),key=lambda x:errs[x],reverse=True):
			f.write(key + "\t" + str(errs[key]) + "\n")

	scores = {"acc":correct/float(total),"baseline":baseline/float(total)}

	return scores


if __name__ == "__main__":
	p = ArgumentParser()
	p.add_argument("--train_list",default=None,help="file with one file name per line of TT SGML training files; all files not in test if not supplied")
	p.add_argument("--test_list",default="test_list.tab",help="file with one file name per line of TT SGML test files")
	p.add_argument("--file_dir",default="tt",help="directory with TT SGML files")
	p.add_argument("--method",default="tt",help="which tagger to use",choices=["tt","marmot","stanford","ensemble"])
	p.add_argument("--retrain",action="store_true",help="whether to retrain")

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

	run_eval(train_list,test_list,tagger=opts.method,retrain=opts.retrain)
