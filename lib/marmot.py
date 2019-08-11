import sys, os, io, platform, subprocess, tempfile, re

PY3 = sys.version_info[0] == 3

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
bin_dir = script_dir + os.sep + ".." + os.sep + "bin" + os.sep
data_dir = script_dir + os.sep + ".." + os.sep + "data" + os.sep
marmot_path = bin_dir + "marmot" + os.sep

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
punctuation = set([".","·","·",":",",","-","ⲻ","·ⲻ","⳾","?",".ⲻ","—","†","=","]","⸱","].","⸓","⳾ⲻ","[","--","·]","··","☧",".]]","[·]","ⲻ·","=–.","̣","."])


def get_col(data, colnum):
	if not isinstance(data,list):
		data = data.split("\n")

	splits = [row.split("\t") for row in data if "\t" in row]
	return [r[colnum] for r in splits]


def inject_col(source_lines, target_lines, col=-1, into_col=None, skip_supertoks=False):

	output = []
	counter = -1
	target_line = ""

	if not PY3:
		if isinstance(target_lines,unicode):
			target_lines = str(target_lines.encode("utf8"))

	if not isinstance(source_lines,list):
		source_lines = source_lines.split("\n")
	if not isinstance(target_lines,list):
		target_lines = target_lines.split("\n")

	for i, source_line in enumerate(source_lines):
		while len(target_line) == 0:
			counter +=1
			target_line = target_lines[counter]
			if (target_line.startswith("<") and target_line.endswith(">")) or len(target_line) == 0:
				output.append(target_line)
				target_line = ""
			else:
				target_cols = target_line.split("\t")
				if "-" in target_cols[0] and skip_supertoks:
					output.append(target_line)
					target_line = ""
		source_cols = source_line.split("\t")
		to_inject = source_cols[col]
		target_cols = target_line.split("\t")
		if into_col is None:
			target_cols.append(to_inject)
		else:
			target_cols[into_col] = to_inject
		output.append("\t".join(target_cols))
		target_line=""

	return "\n".join(output)


def exec_via_temp_twofile(input_text, command_params, workdir="", outfile=False):
	temp = tempfile.NamedTemporaryFile(delete=False)
	if outfile:
		temp2 = tempfile.NamedTemporaryFile(delete=False)
	output = ""
	try:
		if input_text is not None:
			temp.write(input_text.encode("utf8"))
			temp.close()

			if outfile:
				command_params = [x if 'tempfilename2' not in x else x.replace("tempfilename2",temp2.name) for x in command_params]
			command_params = [x if 'tempfilename' not in x else x.replace("tempfilename",temp.name) for x in command_params]
		if workdir == "":
			proc = subprocess.Popen(command_params, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
			(stdout, stderr) = proc.communicate()
		else:
			proc = subprocess.Popen(command_params, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,cwd=workdir)
			(stdout, stderr) = proc.communicate()
		if outfile:
			if PY3:
				output = io.open(temp2.name,encoding="utf8").read()
			else:
				output = open(temp2.name).read()
			temp2.close()
			os.remove(temp2.name)
		else:
			output = stdout
		#print(stderr)
		proc.terminate()
	except Exception as e:
		print(e)
	finally:
		if PY3:
			if not outfile:
				output = output.decode("utf8").replace("\r","")
		if input_text is not None:
			os.remove(temp.name)
		return output


def marmotify(indata,train=False,sent=None,func=False):
	output = []
	counter = 0
	split_next = False
	for line in indata.strip().split("\n"):
		if line.startswith("<") and line.endswith(">"):
			if sent is not None:
				if line == "</" + sent + ">":
					split_next = True
			continue
		if split_next:
			output.append("")
			counter = 0
			split_next = False
		fields = line.split("\t")
		if train:
			if func:
				output.append("\t".join([str(counter),fields[0],fields[1],fields[2]]))
			else:
				output.append("\t".join([str(counter),fields[0],fields[1],"_"]))
		else:
			output.append(line)
		counter +=1
		if sent is None and fields[0] in punctuation:
			output.append("")
			counter = 0
	return "\n".join(output) + "\n"


def tag_marmot(indata,model=None,sent=None,func=False):

	if model is None:
		model = script_dir+"cop.marmot"

	if platform.system() == "Windows":
		tag = ["java","-Dfile.encoding=UTF-8","-Xmx2g","-cp","*;","marmot.morph.cmd.Annotator","-model-file",model,"-test-file","form-index=0,tempfilename","-pred-file","tempfilename2"]
	else:
		tag = ["java","-Dfile.encoding=UTF-8","-Xmx2g","-cp","marmot.jar:trove.jar","marmot.morph.cmd.Annotator","-model-file",model,"-test-file","form-index=0","tempfilename","-pred-file","tempfilename2"]

	to_tag = marmotify(indata,sent=sent)

	tagged = exec_via_temp_twofile(to_tag, tag, workdir=marmot_path, outfile=True)
	tagged = tagged.replace("\n\n","\n").strip()
	if func:
		tags = get_col(tagged,7)
	else:
		tags = get_col(tagged,5)

	if sent is not None:
		indata = re.sub(r'</?'+sent+'>\n*','',indata)

	tagged = inject_col(tags,indata.strip())

	return tagged


def train_marmot(train_data,model=None,func=False):
	train = marmotify(train_data,train=True,func=func)

	if model is None:
		model = script_dir+"cop.marmot"

	if platform.system() == "Windows":
		cmd = ["java","-Xmx4G","-cp","*;","marmot.morph.cmd.Trainer","-train-file","form-index=1,tag-index=2,morph-index=3,tempfilename","-tag-morph","true","-model-file",model]
	else:
		cmd = ["java","-Xmx4G","-cp","marmot.jar:trove.jar","marmot.morph.cmd.Trainer","-train-file","form-index=1,tag-index=2,morph-index=3,tempfilename","-tag-morph","true","-model-file",model]

	exec_via_temp_twofile(train,cmd,workdir=marmot_path)
