import subprocess, tempfile, os, sys,io

PY3 = sys.version_info[0] == 3

def exec_via_temp(input_text, command_params, workdir=""):
	temp = tempfile.NamedTemporaryFile(delete=False)
	exec_out = ""
	try:
		if PY3:
			temp.write(input_text.encode("utf8"))
		else:
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
		return exec_out


def fs_tokenize(bound_groups,rule_nums=False):

	if rule_nums:
		cmd = ["perl",os.path.dirname(os.path.realpath(__file__)) + os.sep + "tokenize_perl.pl","-r","tempfilename"]
	else:
		cmd = ["perl",os.path.dirname(os.path.realpath(__file__)) + os.sep + "tokenize_perl.pl","tempfilename"]
	data = "\n".join(bound_groups)
	tokenized = exec_via_temp(data,cmd,os.path.dirname(os.path.realpath(__file__)) + os.sep)
	#if PY3:
	tokenized = tokenized.decode("utf8")

	if rule_nums:
		tokenized = tokenized.replace("\r","").strip().split("\n")
		rules, tokenized = zip(*[line.split("\t") for line in tokenized])
		return list(tokenized), list([int(r) for r in rules])
	else:
		tokenized = tokenized.replace("\r","").strip().split("\n")
		return tokenized

if __name__ == "__main__":
	groups = io.open(sys.argv[1],encoding="utf8").read().replace("\r","").split("\n")
	tokenized = fs_tokenize(groups)
	tokenized = "\n".join(tokenized) + "\n"
	if PY3:
		sys.stdout.buffer.write(tokenized.encode("utf8"))
	else:
		sys.stdout.write(tokenized.encode("utf8"))
