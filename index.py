#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgitb
from nlp_form import make_nlp_form

cgitb.enable()

print "Content-Type: text/html\n\n\n"
print make_nlp_form("public", "interactive")