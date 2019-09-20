import sys, os, io, platform
from utils.eval_utils import exec_via_temp, get_col, inject_col

PY3 = sys.version_info[0] == 3

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
bin_dir = script_dir + os.sep + ".." + os.sep + "bin" + os.sep
stanford_path = bin_dir + "stanford" + os.sep

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
punctuation = set([".","·","·",":",",","-","ⲻ","·ⲻ","⳾","?",".ⲻ","—","†","=","]","⸱","].","⸓","⳾ⲻ","[","--","·]","··","☧",".]]","[·]","ⲻ·","=–.","̣","."])


def stanfordify(indata,train=False):
	output = []
	sent = []
	for line in indata.strip().split("\n"):
		if " " in line:
			line = line.replace(" ",".")
		fields = line.split("\t")
		if train:
			sent.append("/".join([fields[0],fields[1]]))
		else:
			sent.append(fields[0])
		if fields[0] in punctuation:
			output.append(" ".join(sent))
			sent = []
	if len(sent) > 0:
		output.append(" ".join(sent))
	return "\n".join(output) + "\n"


def unstanfordify(indata):
	output = []
	for line in indata.strip().split("\n"):
		words = line.split(" ")
		for word in words:
			tok, pos = word.split("/")
			output.append("\t".join([tok,pos]))
	return "\n".join(output) + "\n"


def tag_stanford(indata):

	tag = ["java","-mx300m","-cp","stanford-postagger.jar;","edu.stanford.nlp.tagger.maxent.MaxentTagger","-outputFormat","slashTags","-tagSeparator","/","-encoding","utf8","-sentenceDelimiter","newline","-tokenize","false","-model","cop","-textFile","tempfilename"]

	to_tag = stanfordify(indata)

	tagged = exec_via_temp(to_tag, tag, workdir=stanford_path)
	tagged = unstanfordify(tagged)

	return tagged


def train_stanford(train_data):
	train = stanfordify(train_data)

	cmd = ["java","-classpath","stanford-postagger.jar","edu.stanford.nlp.tagger.maxent.MaxentTagger","-prop","cop.props","-trainFile","tempfilename"]

	exec_via_temp(train,cmd,workdir=stanford_path)
