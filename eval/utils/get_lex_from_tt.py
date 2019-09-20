import io, sys, os, re
from glob import glob
from collections import defaultdict
from eval_utils import list_files


script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
data_dir = script_dir + ".." + os.sep + ".." + os.sep + "data" + os.sep


def scrape_sgml(lines,vocab):

	norm = pos = lemma = ""
	for line in lines:
		if ' norm=' in line:
			norm = re.search(r' norm="([^"]*)"',line).group(1)
		if ' pos=' in line:
			pos = re.search(r' pos="([^"]*)"',line).group(1)
		if ' lemma=' in line:
			lemma = re.search(r' lemma="([^"]*)"',line).group(1)
		if "</norm_group>" in line:
			vocab[(norm,pos,lemma)] += 1

	return vocab


vocab = defaultdict(int)

files = list_files("ud_train")
files += list_files("ud_dev")

old_dict = io.open(data_dir + "copt_lemma_lex.tab",encoding="utf8").read().strip().split("\n")
old_lex = set([tuple(line.split("\t")) for line in old_dict])

for file_ in files:
	lines = io.open(file_,encoding="utf8").readlines()

	vocab = scrape_sgml(lines,vocab)

output = []
for tup in sorted(vocab,reverse=True,key=lambda x:vocab[x]):
	if all([len(x)>0 for x in tup]):
		if tup not in old_lex:
			freq = vocab[tup]
			word, pos, lemma = tup
			output.append("\t".join([word,pos,lemma,str(freq)]))

with io.open("new_lex.tab",'w',encoding="utf8") as f:
	f.write("\n".join(output)+"\n")

