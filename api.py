#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-

#from lib.tokenize_rf import MultiColumnLabelEncoder, DataFrameSelector, lambda_underscore

#Example call on localhost:
#http://localhost/coptic-nlp/api.py?data=%E2%B2%81%CF%A5%E2%B2%A5%E2%B2%B1%E2%B2%A7%E2%B2%99%20%E2%B2%9B%CF%AD%E2%B2%93%E2%B2%A1%E2%B2%A3%E2%B2%B1%E2%B2%99%E2%B2%89&lb=line

from nlp_form import nlp_coptic
import cgi
storage = cgi.FieldStorage()
#storage = {"data":"ⲁϥⲥⲱⲧⲙ ⲛϭⲓⲡⲣⲱⲙⲉ"}
if "data" in storage:
	#data = storage["data"]
	data = storage.getvalue("data")
else:
	data = ""

if "lb" in storage:
	line = storage.getvalue("lb")
else:
	if "<lb" in data:
		line = "noline"
	else:
		line = "line"

if "format" in storage:
	format = storage.getvalue("format")
else:
	format = "sgml"

if format != "conll" and format != "pipes" and format != "sgml_no_parse":
	format = "sgml"

if format == "pipes":
	print("Content-Type: text/plain; charset=UTF-8\n")
	processed = nlp_coptic(data,lb=line=="line",sgml_mode="pipes",do_tok=True)
	if "</lb>" in processed:
		processed = processed.replace("</lb>","</lb>\n")
	print(processed.strip())
elif format == "sgml_no_parse":
	print("Content-Type: text/sgml; charset=UTF-8\n")
	# secure call, note that htaccess prevents this running without authentication
	if "|" in data:
		processed = nlp_coptic(data, lb=line=="line", parse_only=False, do_tok=True, do_mwe=False,
							   do_norm=True, do_tag=True, do_lemma=True, do_lang=True,
							   do_milestone=True, do_parse=("no_parse" not in format), sgml_mode="sgml",
							   tok_mode="from_pipes", old_tokenizer=False)
	else:
		processed = nlp_coptic(data, lb=line=="line", parse_only=False, do_tok=True, do_mwe=False,
							   do_norm=True, do_tag=True, do_lemma=True, do_lang=True,
							   do_milestone=True, do_parse=("no_parse" not in format), sgml_mode="sgml",
							   tok_mode="auto", old_tokenizer=False)
	print(processed.strip() + "\n")
elif format != "conll":
	print("Content-Type: text/"+format+"; charset=UTF-8\n")
	processed = nlp_coptic(data,lb=line=="line")
	print("<doc>\n"+processed.strip()+"\n</doc>\n")
else:
	print("Content-Type: text/plain; charset=UTF-8\n")
	processed = nlp_coptic(data,lb=False,parse_only=True,do_tok=True,do_tag=True)
	print(processed.strip())
