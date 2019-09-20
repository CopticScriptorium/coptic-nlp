#!/usr/bin/python3.5
# -*- coding: utf-8 -*-

import cgitb
import sys
cgitb.enable()

from nlp_form import make_nlp_form

PY3 = sys.version_info[0] > 2

if PY3:
	sys.stdout.buffer.write("Content-Type: text/html\n\n\n".encode("utf8"))
	content = make_nlp_form("secure", "interactive")
	sys.stdout.buffer.write(content.encode("utf8"))
else:
	print("Content-Type: text/html\n\n\n")
	content = make_nlp_form("secure", "interactive")
	print(content)
