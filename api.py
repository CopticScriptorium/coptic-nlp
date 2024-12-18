#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import requests
import cgi, sys

PY3 = sys.version_info[0] == 3
if PY3:
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

storage = cgi.FieldStorage()
#storage = {"data": "ⲁϥⲥⲱⲧⲙ ⲛϭⲓⲡⲣⲱⲙⲉ"}
if "data" in storage:
    #data = storage["data"]
    data = storage.getvalue("data")
else:
    data = ""

# Diagnose detokenization needs
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
    format = "sgml_no_parse"

if format not in ["conll", "pipes", "sgml_no_parse", "sgml_entities"]:
    format = "sgml_no_parse"

if "sgml" in format:
    print("Content-Type: text/sgml; charset=UTF-8\n")
else:
    print("Content-Type: text/plain; charset=UTF-8\n")

params = {"data":data,"lb":line,"format":format}
result = requests.post("http://localhost:5555/",params=params)
print(result.content.decode("utf8"))
