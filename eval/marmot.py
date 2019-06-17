import sys, os, io, platform
from utils.eval_utils import exec_via_temp, get_col, inject_col

PY3 = sys.version_info[0] == 3

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
bin_dir = script_dir + os.sep + ".." + os.sep + "bin" + os.sep
marmot_path = "C:\\Uni\\HK\\Taggers\\Marmot\\"
#marmot_path = bin_dir + "marmot" + os.sep

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
punctuation = set([".","·","·",":",",","-","ⲻ","·ⲻ","⳾","?",".ⲻ","—","†","=","]","⸱","].","⸓","⳾ⲻ","[","--","·]","··","☧",".]]","[·]","ⲻ·","=–.","̣","."])


def marmotify(indata,train=False):
	output = []
	counter = 0
	for line in indata.strip().split("\n"):
		fields = line.split("\t")
		if train:
			output.append("\t".join([str(counter),fields[0],fields[1],"_"]))
		else:
			output.append(line)
		counter +=1
		if fields[0] in punctuation:
			output.append("")
			counter = 0
	return "\n".join(output) + "\n"


def tag_marmot(indata):

	if platform.system() == "Windows":
		tag = ["java","-Dfile.encoding=UTF-8","-Xmx2g","-cp","*;","marmot.morph.cmd.Annotator","-model-file",script_dir+"test.marmot","-test-file","form-index=0,tempfilename","-pred-file","tempfilename2"]
	else:
		tag = ["java","-Dfile.encoding=UTF-8","-Xmx2g","-cp","marmot.jar:trove.jar","marmot.morph.cmd.Annotator","-model-file",script_dir+"test.marmot","-test-file","form-index=0","tempfilename","-pred-file","tempfilename2"]

	to_tag = marmotify(indata)

	tagged = exec_via_temp(to_tag, tag, workdir=marmot_path, outfile=True)
	tagged = tagged.replace("\n\n","\n").strip()
	tags = get_col(tagged,5)

	tagged = inject_col(tags,indata.strip())

	return tagged


def train_marmot(train_data):
	train = marmotify(train_data,train=True)

	if platform.system() == "Windows":
		cmd = ["java","-Xmx4G","-cp","*;","marmot.morph.cmd.Trainer","-train-file","form-index=1,tag-index=2,morph-index=3,tempfilename","-tag-morph","true","-model-file",script_dir+"test.marmot"]
	else:
		cmd = ["java","-Xmx4G","-cp","marmot.jar:trove.jar","marmot.morph.cmd.Trainer","-train-file","form-index=1,tag-index=2,morph-index=3,tempfilename","-tag-morph","true","-model-file",script_dir+"test.marmot"]

	exec_via_temp(train,cmd,workdir=marmot_path)
