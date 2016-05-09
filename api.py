#!/usr/bin/python
# -*- coding: utf-8 -*-

#Example call on localhost:
#http://localhost/coptic-nlp/api.py?data=%E2%B2%81%CF%A5%E2%B2%A5%E2%B2%B1%E2%B2%A7%E2%B2%99%20%E2%B2%9B%CF%AD%E2%B2%93%E2%B2%A1%E2%B2%A3%E2%B2%B1%E2%B2%99%E2%B2%89&lb=line

from nlp_form import nlp_coptic
import cgi
storage = cgi.FieldStorage()
if "data" in storage:
	data = storage.getvalue("data")
else:
	data = ""

if "lb" in storage:
	line = storage.getvalue("lb")
else:
	line = "noline"

if "format" in storage:
	format = storage.getvalue("format")
else:
	format = "xml"

if format != "xml" and format != "conll":
	format = "sgml"

if format != "conll":
	print "Content-Type: text/"+format+"; charset=UTF-8\n"
	processed = nlp_coptic(data,line)

	print "<doc>\n"+processed.strip()+"\n</doc>\n"
else:
	print "Content-Type: text/plain; charset=UTF-8\n"
	processed = nlp_coptic(data,line,True)
	print processed.strip()
