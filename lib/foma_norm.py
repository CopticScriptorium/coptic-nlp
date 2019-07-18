#!/usr/bin/python
# -*- coding: utf-8 -*-

import io, os, re, sys
from collections import defaultdict
import tempfile, subprocess
from six import iteritems

PY3 = sys.version_info[0] == 3

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
data_dir = script_dir + ".." + os.sep + "data" + os.sep

orig_chars = set(["̈", "", "̄", "̀", "̣", "`", "̅", "̈", "̂", "︤", "︥", "︦", "⳿", "~", "\n", "̇", " ", "‴", "#", "᷍", "⸍", "›", "‹"])


def clean(text):
	if "(" not in text and ")" not in text:  # Retain square brackets if item has capturing groups
		text = text.replace("[","").replace("]","")
	return ''.join([c for c in text if c not in orig_chars])


def exec_via_temp(input_text, command_params, workdir=""):
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
			proc = subprocess.Popen(command_params, stdout=subprocess.PIPE,stdin=io.open(temp.name,encoding="utf8"),stderr=subprocess.PIPE)
			(stdout, stderr) = proc.communicate()
		else:
			proc = subprocess.Popen(command_params, stdout=subprocess.PIPE,stdin=io.open(temp.name,encoding="utf8"),stderr=subprocess.PIPE,cwd=workdir)
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


class FomaNorm:

	def __init__(self):
		pass

	def normalize(self,origs):
		origs = [clean(orig) for orig in origs]
		cmd = [script_dir+"flookup","-ix",data_dir+"coptic.bin","tempfilename"]
		normalized = exec_via_temp("\n".join(origs),cmd,workdir=script_dir)
		normalized = normalized.strip().split("\n\n")
		normalized = self.disambiguate(normalized,origs)
		for i, orig in enumerate(origs):
			if "?" in normalized[i]:
				normalized[i] = orig

		return normalized

	def disambiguate(self,norms,origs):
		output = []

		for i, norm in enumerate(norms):

			if "\n" not in norm:
				output.append(norm)
				continue
			orig = origs[i]
			options = norm.split("\n")
			found = False
			for opt in options:
				if opt == orig:
					output.append(opt)
					found = True
					break
			if not found:
				output.append(max(options,key=len))
		return output

	def test(self,s,expected):

		norm = self.normalize([s])[0]
		print("'%s' -> %s" % (s, norm), end=' ')
		if norm == expected:
			print("CORRECT")
		else:
			print("***WRONG***, expected %s" % expected)


if __name__ == "__main__":

	fm = FomaNorm()
	fm.test("ⲁⲥⲇⲁⲇⲁⲁ","ⲁⲥⲇⲁⲇⲁⲁ")
	fm.test("ⲉⲧⲃⲉⲧϥⲭⲣⲓⲁ","ⲉⲧⲃⲉⲧⲉϥⲭⲣⲉⲓⲁ")
	fm.test("ⲙⲛⲛϥⲯⲩⲭⲏ","ⲙⲛⲛⲉϥⲯⲩⲭⲏ")
	fm.test("ⲙⲡⲁⲧⲉⲓⲥⲱⲧⲙ","ⲙⲡⲁⲧⲓⲥⲱⲧⲙ")

