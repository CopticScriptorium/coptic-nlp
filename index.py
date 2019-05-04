#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgitb
cgitb.enable()

from nlp_form import make_nlp_form

print("Content-Type: text/html\n\n\n")
print(make_nlp_form("public", "interactive"))
