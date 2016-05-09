#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This script takes CWB-SGML format input
and outputs EtherCalc/SocialCalc spreadsheet data

Author: Amir Zeldes
"""

import re
from collections import defaultdict
from collections import OrderedDict
import cgi

__version__ = "1.0.0"

data = ""
storage = cgi.FieldStorage()
if "data" in storage:
	data = storage.getvalue("data")
else:
	data = ""

data = re.sub('>','>\n',data)
data = re.sub('</','\n</',data)
data = re.sub('\n+','\n',data)


def flush_open(annos, row_num, colmap):
	flushed = ""
	for anno in annos:
		element, name, value = anno
		flushed += "cell:"+colmap[name] + str(row_num) + ":t:" + value + "\n"
	return flushed


def flush_close(closing_element, last_value, last_start, row_num, colmap):
	flushed = ""
	for alias in aliases[closing_element]:
		if last_start[alias] < row_num - 1:
			span_string = ":rowspan:" + str(row_num - last_start[alias])
		else:
			span_string = ""
		flushed += "cell:" + colmap[alias] + str(last_start[alias]) + ":t:" + last_value[alias]+span_string + ":f:1\n"
	return flushed


def number_to_letter(number):
	# Currently support up to 26 columns; no support for multiletter column headers beyond letter Z
	if number < 27:
		return chr(number + ord('a')-1).upper()
	else:
		return None

current_row = 2
open_annos = defaultdict(list)
close_annos = []
aliases = defaultdict(list)
last_value = {}
last_start = {}
colmap = OrderedDict()
maxcol = 1

preamble = """socialcalc:version:1.0
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary=SocialCalcSpreadsheetControlSave
--SocialCalcSpreadsheetControlSave
Content-type: text/plain; charset=UTF-8

# SocialCalc Spreadsheet Control Save
version:1.0
part:sheet
part:edit
part:audit
--SocialCalcSpreadsheetControlSave
Content-type: text/plain; charset=UTF-8

version:1.5
"""
output = ""

for line in data.split("\n"):
	line = line.strip()
	line = line.replace(":","\\c")
	if line.startswith("<?") or line.endswith("/>"):  # Skip unary tags and XML instructions
		pass
	elif line.startswith("</"):  # Closing tag
		my_match = re.match("</([^>]+)>",line)
		element = my_match.groups(0)[0]
		output+=flush_close(element, last_value, last_start, current_row, colmap)
	elif line.startswith("<"): # Opening tag
		my_match = re.match("<([^ >]+)[ >]",line)
		element = my_match.groups(0)[0]
		aliases[element] = []  # Reset element aliases to see which attributes this instance has
		if "=" not in line:
			line = "<" + element + " " + element + '="' + element + '">'

		my_match = re.findall('([^" =]+)="([^"]+)"',line)
		anno_name = ""
		anno_value = ""
		for match in my_match:
			anno_name = match[0]
			anno_value = match[1]
			open_annos[current_row].append((anno_name,anno_value))
			last_value[anno_name] = anno_value
			last_start[anno_name] = current_row
			if element not in aliases:
				aliases[element] = [anno_name]
			elif anno_name not in aliases[element]:
				aliases[element].append(anno_name)
			if anno_name not in colmap:
				maxcol +=1
				colmap[anno_name] = number_to_letter(maxcol)

	elif len(line)>0:  # Token
		token = line.strip()
		output += "cell:A"+str(current_row)+":t:"+token+":f:1\n"
		current_row +=1
	else:  # Empty line
		current_row +=1

print "Content-type: text/plain; charset=UTF-8\n"
print preamble
print "cell:A1:t:tok:f:2"
for header in colmap:
	print "cell:"+colmap[header]+"1:t:"+header+":f:2"
print output


print "sheet:c:" + str(maxcol) + ":r:" + str(current_row) + ":tvf:1"

# Prepare default Antinoou font for Coptic data
print """
font:1:* * Antinoou
font:2:normal bold * *
valueformat:1:text-wiki
--SocialCalcSpreadsheetControlSave
Content-type: text/plain; charset=UTF-8
"""