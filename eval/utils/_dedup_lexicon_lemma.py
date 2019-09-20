import io, sys
from collections import defaultdict

lines = io.open(sys.argv[1],encoding="utf8").readlines()
entries = defaultdict(set)

for line in lines:
	fields = line.strip().split("\t")
	entries[fields[0]].add((fields[1],fields[2]))

keys = sorted(entries.keys())
seen = set([])
discarded = set([])

for key in keys:
	out_line = key + "\t"
	analyses = []
	for pos, lemma in sorted(entries[key]):
		if (key,pos) not in seen:
			analyses.append(pos + "\t" + lemma)
			seen.add((key,pos))
		else:
			discarded.add((key,pos,lemma))
	out_line += "\t".join(analyses) + "\n"
	sys.stdout.buffer.write(out_line.encode("utf8"))

with io.open("discarded.tab",'w', encoding="utf8",newline="\n") as f:
	for tup in discarded:
		f.write("\t".join(tup) + "\n")