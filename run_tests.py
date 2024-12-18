"""Unit tests for Coptic NLP"""

import io, re, os, sys, platform, zipfile
from collections import defaultdict
from six import iterkeys

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
data_dir = script_dir + "data" + os.sep
lib_dir = script_dir + "lib" + os.sep
bin_dir = script_dir + "bin" + os.sep

from coptic_nlp import nlp_coptic
from lib.stacked_tokenizer import StackedTokenizer

PY3 = sys.version_info[0] == 3

# Check requirements
if not (os.path.exists(bin_dir + "foma" + os.sep + "flookup") or os.path.exists(bin_dir + "foma" + os.sep + "flookup.exe")):
	sys.stderr.write("! Foma flookup not found at ./bin/foma/\n! Attempting to obtain from zip...")
	if platform.system() == "Windows":
		with zipfile.ZipFile(bin_dir + "foma" + os.sep + "foma_win.zip", 'r') as z:
			z.extractall(bin_dir + "foma" + os.sep)
	elif platform.system() == "Darwin":
		with zipfile.ZipFile(bin_dir + "foma" + os.sep + "foma_osx.zip", 'r') as z:
			z.extractall(bin_dir + "foma" + os.sep)
	else:  # Linux
		sys.stderr.write("! Need to compile foma on Linux and place flookup in bin/foma/\n! See bin/foma/README.md \n")
		sys.exit(0)
	sys.stderr.write("! Foma flookup extracted to bin/foma/\n")

class CopticTest:

	def __init__(self):
		self.tests = defaultdict(list)
		self.total = 0
		self.success = 0

	def add_test(self,data,expected_out,flags,comment):
		self.tests[flags].append((data,expected_out,comment))

	def run_tests(self):
		stk = StackedTokenizer(pipes=True,
							   segment_merged=False, detok=0, ambig=data_dir + "ambig.tab")
		for test in sorted(list(iterkeys(self.tests))):
			sys.stderr.write("o Testing configuration: " + test + "\n")
			all_inputs = ""
			for tup in self.tests[test]:
				data, _, _ = tup
				if not data.endswith("_"):
					data = data.strip()+"_"
				all_inputs += data + "\n"
			flags = test.strip().split(" ")
			sgml_mode = "pipes" if "pipes" in flags else "sgml"
			if sgml_mode == "pipes":
				stk.pipes = True
			else:
				stk.pipes = False
			tok_mode = "from_pipes" if "from_pipes" in flags else "auto"
			if tok_mode == "from_pipes":
				stk.tokenized = True
			else:
				stk.tokenized = False
			detokenize = 0
			norm = multiword = tag = lemma = etym = unary = parse = False
			if "-penmult" in flags:
				norm = multiword = tag = lemma = etym = unary = parse = True
			if "-enult" in flags:
				norm = tag = lemma = etym = True

			if "-d" in flags:
				aggressive = False
				if "1" in flags:
					detokenize = 1
				elif "2" in flags:
					detokenize = 2
					aggressive = True
				elif "3" in flags:
					detokenize = 3
				stk.detokenize = detokenize
				stk.load_detokenizer(aggressive=aggressive)

			segment_merged = False

			nlp_resp = nlp_coptic(all_inputs, do_tok=True,
							   do_norm=norm, do_mwe=multiword, do_tag=tag, do_lemma=lemma,
							   do_lang=etym, do_milestone=unary, do_parse=parse, sgml_mode=sgml_mode,
							   tok_mode=tok_mode, preloaded=None,#{"stk":stk},
							   detokenize=detokenize,
							   segment_merged=segment_merged)

			for tup in self.tests[test]:
				_, expected, comment = tup
				self.total += 1
				self.success += self.compare(nlp_resp,expected,comment)

		sys.stderr.write("\nFinished " + str(self.total) + " tests (" + str(self.success)+"/" + str(self.total) +" successful)\n")

	def compare(self,response,expected,comment):
		if len(comment) > 0:
			sys.stderr.write("\t" + comment + "\n")
		if expected in response:
			sys.stderr.write("\t\tPASS\n")
			return 1
		else:
			sys.stderr.write("\t\tFAIL (expected: "+ expected + ")\n")
			return 0


lines = io.open(data_dir+"tests.dat",encoding="utf8").read().strip()
lines = re.sub(r"\t+","\t",lines)
lines = lines.split("\n")

t = CopticTest()
comment = ""
flags = "-o pipes"

for line in lines:
	if line.strip().startswith("#"):
		comment = line.replace("#","").strip()
	elif "\t" in line:
		fields = line.strip().split("\t")
		if fields[0].strip().startswith("flags"):
			flags = fields[1].strip()
		else:
			t.add_test(fields[0].strip(),fields[1].strip(),flags=flags,comment=comment)
			comment = ""

t.run_tests()
