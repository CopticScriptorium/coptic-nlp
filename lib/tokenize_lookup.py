import csv, os, io, sys

PY3 = sys.version_info[0] > 2

def lookup_tokenize(norms,underscore_oov=False,seg_table=None):
	if seg_table is None:
		seg_table = os.path.dirname(os.path.realpath(__file__)) + os.sep +".." + os.sep + "data" +os.sep+"segmentation_table.tab"
	try:
		reader = csv.reader(open(seg_table, encoding="utf8"), delimiter='\t', escapechar="\\")
	except TypeError:
		reader = csv.reader(io.open(seg_table,encoding="utf8"), delimiter='\t', escapechar="\\")

	if PY3:
		segs = dict((rows[0], rows[1]) for rows in reader)
	else:
		segs = dict((rows[0].decode("utf8"), rows[1].decode("utf8")) for rows in reader)

	tokenized = []

	for norm in norms:
		if norm in segs:
			tokenized.append(segs[norm])
		else:
			if underscore_oov:
				tokenized.append("_")
			else:
				tokenized.append(norm)

	return tokenized
