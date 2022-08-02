#!/usr/bin/python
# -*- coding: utf-8 -*-

#Example call on localhost:
#http://localhost/coptic-nlp/api.py?data=%E2%B2%81%CF%A5%E2%B2%A5%E2%B2%B1%E2%B2%A7%E2%B2%99%20%E2%B2%9B%CF%AD%E2%B2%93%E2%B2%A1%E2%B2%A3%E2%B2%B1%E2%B2%99%E2%B2%89&lb=line

from nlp_form import nlp_coptic
import cgi, sys, re

PY3 = sys.version_info[0] == 3
if PY3:
	sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

storage = cgi.FieldStorage()
#storage = {"data":"ⲁϥⲥⲱⲧⲙ ⲛϭⲓⲡⲣⲱⲙⲉ"}
if "data" in storage:
	#data = storage["data"]
	data = storage.getvalue("data")
else:
	data = ""

# Diagnose detokenization needs
detok = 0
segment_merged = False
orig_chars = ["̈", "", "̄", "̀", "̣", "`", "̅", "̈", "̂", "︤", "︥", "︦", "⳿", "~", "\n", "[", "]", "̇", "᷍", "⸍", "›", "‹"]
clean = "".join([c for c in data if c not in orig_chars])
clean = re.sub(r'<[^<>]+>','',clean).replace(" ","_").replace("\n","").lower()
preps = clean.count("_ϩⲛ_") + clean.count("_ⲙⲛ_")
if preps > 4:
	detok = 1
	segment_merged = True

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

if format not in ["conll", "pipes", "sgml_no_parse", "sgml_entities"]:
	format = "sgml"

if format == "pipes":
	print("Content-Type: text/plain; charset=UTF-8\n")
	processed = nlp_coptic(data,lb=line=="line",sgml_mode="pipes",do_tok=True, detokenize=detok, segment_merged=segment_merged)
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
elif format == "sgml_entities":
	print("Content-Type: text/sgml; charset=UTF-8\n\n")
	# secure call, note that htaccess prevents this running without authentication
	processed = nlp_coptic(data, lb=line == "line", parse_only=False, do_tok=False, do_mwe=False,
						   do_norm=False, do_tag=False, do_lemma=False, do_lang=False, sent_tag="translation",
						   do_milestone=True, do_parse=False, sgml_mode="sgml", merge_parse=True,
						   tok_mode="auto", old_tokenizer=False, do_entities=True, pos_spans=True, preloaded={"stk":"","xrenner":None})
	print(processed.strip() + "\n")
elif format != "conll":
	print("Content-Type: text/"+format+"; charset=UTF-8\n")
	processed = nlp_coptic(data,lb=line=="line")
	print("<doc>\n"+processed.strip()+"\n</doc>\n")

else:
	print("Content-Type: text/plain; charset=UTF-8\n")
	processed = nlp_coptic(data,lb=False,parse_only=True,do_tok=True,do_tag=True)
	print(processed.strip())

