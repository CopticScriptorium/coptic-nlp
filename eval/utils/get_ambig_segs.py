import io, sys, os
from collections import defaultdict

lines = io.open(".." + os.sep + "_tmp_train.tab",encoding="utf8").readlines()
entries = defaultdict(lambda:defaultdict(int))

for line in lines:
	line = line.strip()
	if "\t" in line:
		fields = line.split("\t")
		group, analysis = fields
		entries[group][analysis]+=1

output = []
for entry in entries:
	if len(entries[entry])>1:
		if len([entries[entry][x] for x in entries[entry] if entries[entry][x]>2])>1:
			for analysis in entries[entry]:
				output.append(entry + "\t" + analysis +"\t" + str(entries[entry][analysis]))

with io.open("ambig.tab",'w',encoding="utf8") as f:
	f.write("\n".join(output) + "\n")
