#!/usr/bin/python
#  -*- coding: utf-8 -*-

import csv, os, sys, io

PY3 = sys.version_info[0] == 3


class MorphAnalyzer:
	def __init__(self,morph_table=None):
		if morph_table is None:
			morph_table = os.path.dirname(os.path.realpath(__file__)) +os.sep+".."+os.sep+"data" +os.sep+"morph_table.tab"
		try:
			reader = csv.reader(io.open(morph_table, encoding="utf8"), delimiter='\t', escapechar="\\")
		except TypeError:
			reader = csv.reader(open(morph_table), delimiter='\t', escapechar="\\")
		if PY3:
			self.segs = dict((rows[0], rows[1].replace("|","-")) for rows in reader)
		else:
			self.segs = dict((rows[0].decode("utf8"), rows[1].decode("utf8").replace("|","-")) for rows in reader)

	def analyze_morph(self, norms):

		analyzed = []

		#norms2 = norms.decode("utf8").split("|")
		if not PY3:
			pass
			#norms = unicode(norms.decode("utf8"))
			#norms = unicode(norms)

		norms = norms.split("|")

		for norm in norms:
			if norm in self.segs:
				analysis = self.segs[norm]
			#mnt
			elif norm.startswith("ⲙⲛⲧⲁⲧ"):
				analysis = norm.replace("ⲙⲛⲧⲁⲧ","ⲙⲛⲧ-ⲁⲧ-")
			elif norm.startswith("ⲙⲛⲧⲣⲉϥ"):
				analysis = norm.replace("ⲙⲛⲧⲣⲉϥ","ⲙⲛⲧ-ⲣⲉϥ-")
			elif norm.startswith("ⲙⲛⲧ"):
				analysis = norm.replace("ⲙⲛⲧ","ⲙⲛⲧ-")  #might overgenerate

			#ref
			elif norm.startswith("ⲣⲉϥⲣ"):
				analysis = norm.replace("ⲣⲉϥⲣ","ⲣⲉϥ-ⲣ-")
			elif norm.startswith("ⲣⲉϥ"):
				analysis = norm.replace("ⲣⲉϥ","ⲣⲉϥ-")

			#VN compounds
			elif norm.startswith("ϣⲣⲡ") and len(norm) > 3:
				analysis = norm.replace("ϣⲣⲡ", "ϣⲣⲡ-")
			## TODO
			#elsif($strUnit =~ /^($verblist)($nounlist)$/o) { if(length($1)>2){$strUnit = $1 . "|" . $2;}} #might overgenerate

			else:
				analysis = norm
			if analysis.startswith("-"):
				analysis=analysis[1:]
			if analysis.endswith("-"):
				analysis=analysis[:-1]
			analyzed.append(analysis)

		return "|".join(analyzed)
