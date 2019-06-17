from argparse import ArgumentParser
import sys, io, os, re, tempfile, subprocess
from depedit import DepEdit

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
bin_dir = script_dir + ".." + os.sep + "bin" + os.sep
data_dir = script_dir + ".." + os.sep + "data" + os.sep
parser_path = bin_dir + "maltparser-1.8" + os.sep

PY3 = sys.version_info[0] == 3


def exec_via_temp(input_text, command_params, workdir=""):
	temp = tempfile.NamedTemporaryFile(delete=False)
	exec_out = ""
	try:
		temp.write(input_text.encode("utf8"))
		temp.close()

		command_params = [x if x != 'tempfilename' else temp.name for x in command_params]
		if workdir == "":
			proc = subprocess.Popen(command_params, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
			(stdout, stderr) = proc.communicate()
		else:
			proc = subprocess.Popen(command_params, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,cwd=workdir)
			(stdout, stderr) = proc.communicate()

		exec_out = stdout
	except Exception as e:
		print(e)
	finally:
		os.remove(temp.name)
		if PY3:
			exec_out = exec_out.decode("utf8")
		return exec_out


def run_eval(train_list, test_list, retrain=True, method="malt"):

	d = DepEdit(config_file=data_dir + "add_ud_and_flat_morph.ini",options=type('', (), {"quiet":True,"kill":"both"})())

	train = ""
	for file_ in train_list:
		train += io.open(file_,encoding="utf8").read()

	train = train.split("\n")
	train = d.run_depedit(train)

	test_gold = ""
	for file_ in test_list:
		test_gold += io.open(file_,encoding="utf8").read()

	# Remove supertokens and comments with empty-rule depedit
	d = DepEdit(options=type('', (), {"quiet":True,"kill":"both"})())
	test_gold = d.run_depedit(test_gold.split("\n"))
	test_gold = test_gold.split("\n")


	test_blank = []
	for line in test_gold:
		if "\t" in line:
			fields = line.split("\t")
			fields[6:] = ["_","_","_","_"]
		test_blank.append(line)

	test_blank = d.run_depedit(test_blank)

	cmd = ["java","-jar","maltparser-1.8.jar","-c","temp","-i","tempfilename",
		   "-F",r"C:\Uni\Coptic\git\corpora\treebank-dev\v2.1parser\addMergPOSTAGS0FORMStack0.xml",
		   "-m","learn","-grl","root","-pcr","none","-a","nivrestandard","-pp","head","-nr",
		   "true","-ne","false"]

	# Train the parser
	exec_via_temp(train,cmd,parser_path)

	# Test
	cmd = ['java','-mx512m','-jar',"maltparser-1.8.jar",'-c','temp','-i','tempfilename','-m','parse']
	parsed = exec_via_temp(test_blank,cmd,parser_path)
	parsed = parsed.replace("\r","")

	total=0
	correct_head=0
	correct_label=0
	correct_both=0
	for i, line in enumerate(parsed.split("\n")):
		gold_line = test_gold[i]
		if "\t" in line:
			total +=1
			pred = line.split("\t")
			gold = gold_line.split("\t")
			if gold[6] == pred[6] or (pred[7] == "punct" and gold[7] == "punct"):
				correct_head+=1
			if gold[7] == pred[7]:
				correct_label+=1
			if gold[6:8] == pred[6:8] or (pred[7] == "punct" and gold[7] == "punct"):
				correct_both+=1

	total = float(total)
	acc = correct_both/total
	lab = correct_label/total
	attach = correct_head/total
	print("Label accuracy: " + str(lab))
	print("Attach accuracy: " + str(attach))
	print("LAS: " + str(acc))

	results = {"acc":acc, "lab":lab, "attach":attach}

	return results


if __name__ == "__main__":
	p = ArgumentParser()
	p.add_argument("--train_list",default="ud_dev_train",help="file with one file name per line of conll10 training files or alias such as 'ud_train', 'ud_dev_train'")
	p.add_argument("--test_list",default="ud_test",help="file with one file name per line of conll10 training files or alias such as 'ud_train', 'ud_dev_train'")
	p.add_argument("--file_dir",default=None,help="directory with Coptic Treebank files")
	p.add_argument("--method",default="malt",choices=["malt"],help="parser to use")
	p.add_argument("--retrain",action="store_true",help="whether to retrain the parser")

	opts = p.parse_args()

	if opts.file_dir is None:
		file_dir = script_dir + "parses" + os.sep
	else:
		file_dir = opts.file_dir
		if not file_dir.endswith(os.sep):
			file_dir += os.sep

	if os.path.isfile(opts.test_list):
		test_list = io.open(opts.test_list,encoding="utf8").read().strip().split("\n")
		test_list = [script_dir + opts.file_dir + os.sep + f for f in test_list]
	elif opts.test_list.lower() == "ud_test":
		test_list = [file_dir + "cop_scriptorium-ud-test.conllu"]
	else:
		sys.stderr.write("o Unknown test set: " + str(opts.test_list) + "\n")
		sys.exit(0)

	if os.path.isfile(opts.train_list):
		train_list = io.open(opts.train_list,encoding="utf8").read().strip().split("\n")
		train_list = [file_dir + os.sep + f for f in train_list]
	elif opts.train_list.lower() == "ud_train":
		train_list = [file_dir + "cop_scriptorium-ud-train.conllu"]
	elif opts.train_list.lower() == "ud_dev_train":
		train_list = [file_dir + "cop_scriptorium-ud-train.conllu",file_dir + "cop_scriptorium-ud-dev.conllu"]
	else:
		sys.stderr.write("o Unknown train set: " + str(opts.train_list) + "\n")
		sys.exit(0)

	run_eval(train_list,test_list,retrain=opts.retrain)
