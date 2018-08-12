#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os, io
from glob import glob


fixed_meta = '<meta corpus="shenoute.obliged" repo="CopticScriptorium/shenoute-canon6-dev" assigned="somiyagawa" '+ \
	'annotation="So Miyagawa, Julien Delhez, Amir Zeldes" language="Sahidic Coptic" author="Shenoute" country="Egypt" ' +\
	'msContents_title_type="canon" msContents_title_n="6" msItem_title="Then I Am Not Obliged" msName="MONB.XM" '+\
	'objectType="codex" project="CoptOT, Coptic SCRIPTORIUM, KELLIA" translation="Émile Amélineau, So Miyagawa" '+\
	'version_date="2018-07-01" version_n="2.6.0">'

def reorder(lines, add_fixed_meta=False):
	meta_start=""
	contents = lines
	for line in lines:
		if line.startswith("<meta"):
			meta_start = line

	if add_fixed_meta:
		meta_start = fixed_meta

	if "</meta>" in lines or add_fixed_meta:
		if meta_start in lines:
			lines.remove(meta_start)
		if "</meta>" in lines:
			lines.remove("</meta>")
		contents = [meta_start] + lines + ["</meta>"]
	contents = "\n".join(contents) + "\n"
	return contents

if __name__ == "__main__":

	indir = sys.argv[1]
	outdir = sys.argv[2]

	extension = "tt"

	infiles = glob(indir + os.sep + "*." + extension)
	meta_start = ""

	for file_ in infiles:
		outfile = os.path.basename(file_)
		outfile = outdir + os.sep + outfile

		outhandle = io.open(outfile,'w',encoding="utf8",newline="\n")

		lines = io.open(file_,encoding="utf8").read().replace("\r","").strip().split("\n")

		contents = reorder(lines)

		outhandle.write(contents)
		outhandle.close()