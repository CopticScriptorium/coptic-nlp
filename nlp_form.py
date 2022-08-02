#!/usr/bin/python
# -*- coding: utf-8 -*-

# V2.0.0

#print("Content-type: text/html\n\n")

import re, sys, io
import cgi
import requests
import platform
from coptic_nlp import nlp_coptic

PY3 = sys.version_info[0] > 2


def get_menu():
	head = "http://copticscriptorium.org/header.html"
	try:
		header = requests.get(head).text
	except:
		header = ""
	foot = "http://copticscriptorium.org/footer.html"
	try:
		footer = requests.get(foot).text
	except:
		footer = ""
	header = header.replace('href="/','href="http://copticscriptorium.org/')
	footer = re.sub(r'<p id="lastupdate">.*?</p>.*<script>.*lastupdate.*?</script>','',footer,flags=re.DOTALL)

	return header, footer


def make_nlp_form(access_level, mode):
	if platform.system() == 'Linux':
		action_dest = ''
		secure_dest = 'secure'
	else:
		action_dest = 'index.py'
		secure_dest = 'secure.py'


	if access_level == "secure":
		access_message = """				<p>Enter Coptic text in UTF-8 (XML markup is also allowed). <br/>
				Bound groups should be separated by <b>spaces</b> or <b>underscores</b>.</p>"""
		action_dest = secure_dest
	else:
		access_message = '''			<p>Enter Coptic text in UTF-8 (XML markup is also allowed, 10,000 characters max). <br/>
				Bound groups should be separated by <b>spaces</b> or <b>underscores</b>.</p>
				<p>If you need to analyze longer texts or multiple texts automatically, you can log in
				to the <a href="'''+secure_dest+'''">secure</a> area or use the <a href="api">API</a>. For a login please
				contact <a href="http://corpling.uis.georgetown.edu/amir/">Amir Zeldes</a>.
				</p>'''

	if mode == "interactive":
		output = ""
		data = """ⲁ<hi rend="red">ϥ</hi>ⲥⲱⲧ︤ⲙ︥ ⲛⲥⲱϥ ⲛ̄ϭ
ⲓⲡⲁⲅⲅⲉⲗⲟⲥ ⲙ̄ⲙ︤ⲛ︦ⲧ︥ϣⲃⲏⲣ"""
		data += """ . \nⲱ̂ ⲧⲉⲧ︤ⲛ︥ⲣⲱϣⲉ ⲛ̄ⲧⲱⲧ︤ⲛ︥ ⲛⲉⲧⲕⲁⲙⲁ⳿ ⲙ̄ⲡⲥⲁⲧⲁⲛⲁⲥ 
ⲉⲧⲣⲉϥⲉⲓ̂ ⲉϩⲟⲩⲛ ⲛ︤ϥ︥ϫⲱϩ︤ⲙ︥ ⲛ̄ⲙ̄ⲙⲁ ⲉⲧⲟⲩⲁⲁⲃ 
ⲙ̄ⲡⲛⲟⲩⲧⲉ · ⲁⲩⲱ ⲛ̄ⲧⲉⲧ︤ⲛ︥ⲥⲱⲱϥ ⲙ̄ⲡⲉϥⲣ̄ⲡⲉ 
ⲉⲧⲉⲛ̄ⲧⲱⲧ︤ⲛ︥ ⲡⲉ ⲙ̄ⲙⲓⲛⲙ̄ⲙⲱⲧ︤ⲛ︥ · ⲙ̄ⲡⲉⲧ︤ⲛ︥ⲣ̄ⲡⲙⲉⲉⲩⲉ 
ⲛ̄ⲧⲁⲡⲟⲫⲁⲥⲓⲥ ⲙ̄ⲡⲁⲡⲟⲥⲧⲟⲗⲟⲥ 
ϫⲉⲡⲉⲧⲛⲁⲥⲱⲱϥ⳿ ⲙ̄ⲡⲉⲣⲡⲉ ⲙ̄ⲡⲛⲟⲩⲧⲉ ."""
		if not PY3:
			data = data.decode("utf8")
		#form = {}
		form = cgi.FieldStorage()
		processed=""
		lb = "noline"
		old_tok = False
		sgml_mode = "sgml"
		tok_mode = "auto"
		do_lemma = True
		do_tag = True
		do_parse = True
		do_entities = True
		detok = 0
		segment_merged = False
		do_tok = True
		do_norm = True
		do_mwe = True
		do_lang = True
		do_milestone = True
		if "data" in form:
			data = form.getvalue("data")
			data = re.sub(r'\r','',data)
			data = data.strip()
			lb = form.getvalue("lb")
			old_tok = form.getvalue("old_tok") is not None
			sgml_mode = form.getvalue("sgml_mode")
			tok_mode = form.getvalue("tok_mode")
			do_milestone = form.getvalue("milestone") is not None
			do_lemma = form.getvalue("lemma") is not None
			do_tag = form.getvalue("tag") is not None
			do_parse = form.getvalue("parse") is not None
			do_entities = form.getvalue("entities") is not None
			do_norm = form.getvalue("norm") is not None
			do_mwe = form.getvalue("mwe") is not None
			if form.getvalue("laytonize") == "aggressive":
				detok = 2
			elif form.getvalue("laytonize") == "smart":
				detok = 3
			elif form.getvalue("laytonize") == "conservative":
				detok = 1
			else:
				detok = 0
			segment_merged = form.getvalue("segment_merged") is not None
			do_tok = form.getvalue("tok") is not None
			do_lang = form.getvalue("lang") is not None
			if sgml_mode == "pipes":
				do_tok = True

			if len(data) > 20000 and access_level != "secure":
				processed = "Input was too long; demo version limited to 10000 characters"
			else:
				processed = nlp_coptic(data,lb=lb=="line",parse_only=False,do_tok=do_tok,do_norm=do_norm,do_mwe=do_mwe,
									   do_tag=do_tag, do_lemma=do_lemma,do_lang=do_lang,do_milestone=do_milestone,
									   do_parse=do_parse, do_entities=do_entities, sgml_mode=sgml_mode,
									   tok_mode=tok_mode,old_tokenizer=old_tok,
									   detokenize=detok, segment_merged=segment_merged)
				processed = processed.strip()

		###
		"""
		form = {"data":data,"tok":True}
		if "data" in form:
			processed = nlp_coptic(data, lb=lb, parse_only=False, do_tok=do_tok, do_norm=do_norm, do_mwe=do_mwe, do_tag=do_tag,
								   do_lemma=do_lemma, do_lang=do_lang, do_milestone=do_milestone, do_parse=do_parse,
								   sgml_mode=sgml_mode, tok_mode=tok_mode, old_tokenizer=False)
		"""
		###

		data = re.sub(r'\r','',data)



		noline_checked = ' checked="checked"' if lb else ""
		tok_checked = ' checked="checked"' if do_tok else ""
		old_checked = ' checked="checked"' if old_tok else ""
		segment_merged_checked = ' checked="checked"' if segment_merged else ""
		detokenize_checked = ' checked="checked"' if detok > 0 else ""
		laytonize_conservative_checked = ' checked="checked"' if detok == 1 else ""
		laytonize_aggressive_checked = ' checked="checked"' if detok == 2 else ""
		laytonize_smart_checked = ' checked="checked"' if detok == 3 else ""
		auto_checked = ' checked="checked"' if tok_mode == "auto" else ""
		pipes_checked = ' checked="checked"' if tok_mode == "from_pipes" else ""
		norm_checked = ' checked="checked"' if do_norm else ""
		mwe_checked = ' checked="checked"' if do_mwe else ""
		tag_checked = ' checked="checked"' if do_tag else ""
		lemma_checked = ' checked="checked"' if do_lemma else ""
		parse_checked = ' checked="checked"' if do_parse else ""
		entities_checked = ' checked="checked"' if do_entities else ""
		lang_checked = ' checked="checked"' if do_lang else ""
		milestone_checked = ' checked="checked"' if do_milestone else ""
		sgml_checked = ' checked="checked"' if sgml_mode == "sgml" else ""
		justpipes_checked = ' checked="checked"' if sgml_mode == "pipes" else ""
		header, footer = get_menu()

		if access_level == "secure":
			access_js = """						document.getElementById("nlp_form").submit();
						return true;
						"""
		else:
			access_js = """
					if (document.getElementById("data").value.length > 10000){
						alert("You entered " + document.getElementById("data").value.length + " characters. Please enter no more than 10000 characters.");
						return false;
					}
					else{

						document.getElementById("nlp_form").submit();
						return true;
					}"""

		template = io.open("nlp_form.html",encoding="utf8").read()
		template = template.replace("**navbar**", header)
		template = template.replace("**footer**", footer)
		template = template.replace("**action_dest**", action_dest)
		template = template.replace("**access_message**", access_message)
		template = template.replace("**noline_checked**", noline_checked)
		template = template.replace("**sgml_checked**", sgml_checked)
		template = template.replace("**old_checked**", old_checked)
		template = template.replace("**milestone_checked**", milestone_checked)
		template = template.replace("**tok_checked**", tok_checked)
		template = template.replace("**detokenize_checked**", detokenize_checked)
		template = template.replace("**laytonize_conservative_checked**", laytonize_conservative_checked)
		template = template.replace("**laytonize_aggressive_checked**", laytonize_aggressive_checked)
		template = template.replace("**laytonize_smart_checked**", laytonize_smart_checked)
		template = template.replace("**segment_merged_checked**", segment_merged_checked)
		template = template.replace("**auto_checked**", auto_checked)
		template = template.replace("**pipes_checked**", pipes_checked)
		template = template.replace("**norm_checked**", norm_checked)
		template = template.replace("**mwe_checked**", mwe_checked)
		template = template.replace("**tag_checked**", tag_checked)
		template = template.replace("**lemma_checked**", lemma_checked)
		template = template.replace("**parse_checked**", parse_checked)
		template = template.replace("**entities_checked**", entities_checked)
		template = template.replace("**lang_checked**", lang_checked)
		template = template.replace("**noline_checked**", noline_checked)
		template = template.replace("**sgml_checked**", sgml_checked)
		template = template.replace("**justpipes_checked**", justpipes_checked)
		template = template.replace("**data**", data)
		template = template.replace("**processed**", processed)
		template = template.replace("**access_js**", access_js)
		if not PY3:
			template = template.encode("utf8")

		return template
