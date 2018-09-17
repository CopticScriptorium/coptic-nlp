#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgitb
cgitb.enable()

from lib.tokenize_rf import MultiColumnLabelEncoder, DataFrameSelector, lambda_underscore
from nlp_form import make_nlp_form

print("Content-Type: text/html\n\n\n")
print(make_nlp_form("secure", "interactive"))
