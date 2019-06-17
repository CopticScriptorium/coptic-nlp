import sys, os, io
from utils.eval_utils import exec_via_temp

PY3 = sys.version_info[0] == 3

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
utils_dir = script_dir + os.sep + "utils" + os.sep
data_dir = script_dir + os.sep + ".." + os.sep + "data" + os.sep
bin_dir = script_dir + os.sep + ".." + os.sep + "bin" + os.sep
tt_path = bin_dir + "TreeTagger" + os.sep + "bin" + os.sep


def tag_tt(indata):
	model=script_dir+"temp.par"
	cmd = [tt_path + "tree-tagger","-token","-lemma","-no-unknown","-cap-heuristics","-hyphen-heuristics",model,"tempfilename"]
	tagged = exec_via_temp(indata, cmd)
	return tagged


def train_tt(indata):
	# Setup fresh lexicon
	lex_cmd = ["python",utils_dir + "_dedup_lexicon_lemma.py",data_dir+"copt_lemma_lex.tab"]
	lex = exec_via_temp(None, lex_cmd)
	with io.open(script_dir + "lexicon.txt",'w',encoding="utf8",newline="\n") as f:
		f.write(lex)
	lexicon = script_dir + "lexicon.txt"
	open_class = script_dir + "coptic_open_classes.tab"
	cmd = [tt_path + "train-tree-tagger","-st","PUNCT","-cl","3",lexicon,open_class,"tempfilename",script_dir+"temp.par"]
	exec_via_temp(indata, cmd)
