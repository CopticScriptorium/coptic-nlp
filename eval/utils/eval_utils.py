import tempfile, subprocess
import io, os, sys
from glob import glob

PY3 = sys.version_info[0] == 3

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
eval_dir = script_dir + ".." + os.sep


def exec_via_temp(input_text, command_params, workdir="", outfile=False):
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


def exec_via_temp_old(input_text, command_params, workdir=""):
	exec_out = ""
	try:
		if input_text is not None:
			temp = tempfile.NamedTemporaryFile(delete=False)
			if PY3:
				# try:
				temp.write(input_text.encode("utf8"))
				# except:
				# 	temp.write(input_text)
			else:
				temp.write(input_text)
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
		if input_text is not None:
			os.remove(temp.name)
		if PY3:
			try:
				exec_out = exec_out.decode("utf8").replace("\r","")
			except:
				pass
		return exec_out


def list_files(alias="silver",file_dir=None,parse=False):

	if file_dir is None:
		file_dir = eval_dir + "tt" + os.sep # Default tt file directory

	file_list = []
	if parse:
		file_dir = eval_dir + "parses" + os.sep
		if alias.lower() == "ud_test":
			file_list = [file_dir + "cop_scriptorium-ud-test.conllu"]
		elif alias.lower() == "ud_train":
			file_list = [file_dir + "cop_scriptorium-ud-train.conllu"]
		elif alias.lower() == "ud_dev_train":
			file_list = [file_dir + "cop_scriptorium-ud-train.conllu",file_dir + "cop_scriptorium-ud-dev.conllu"]
	else:
		if alias.lower() == "cyrus":
			file_dir = eval_dir + "unreleased" + os.sep
			file_list = [file_dir + "BritMusOriental6783_part1.tt",file_dir + "BritMusOriental6783_part2.tt"]
		elif alias.lower() == "cyrus_plain":
			file_dir = eval_dir + "plain" + os.sep
			file_list = [file_dir + "BritMusOriental6783_part1.txt",file_dir + "BritMusOriental6783_part2.txt"]
		elif alias.lower() == "ud_test":
			file_list = io.open(eval_dir + "test_list.tab").read().strip().split("\n")
			file_list = [file_dir + f for f in file_list]
		elif alias.lower() == "ud_dev":
			file_list = io.open(eval_dir + "dev_list.tab").read().strip().split("\n")
			file_list = [file_dir + f for f in file_list]
		elif alias.lower() == "ud_train":
			file_list = io.open(eval_dir + "train_list.tab").read().strip().split("\n")
			file_list = [file_dir + f for f in file_list]
		elif alias.lower() == "victor_plain":
			file_dir = eval_dir + "plain" + os.sep
			file_list = [file_dir + "martyrdom.victor.txt"]
		elif alias.lower() == "victor_tt":
			file_dir = eval_dir + "plain" + os.sep
			file_list = [file_dir + "martyrdom.victor.01.tt"]
		elif alias.lower() == "silver":
			test_list = io.open(eval_dir + "test_list.tab").read().strip().split("\n")
			file_list = glob(file_dir + os.sep + "*.tt")
			filtered = []
			for f in file_list:
				if os.path.basename(f) not in test_list:
					filtered.append(f)
			file_list = filtered

	return file_list


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
