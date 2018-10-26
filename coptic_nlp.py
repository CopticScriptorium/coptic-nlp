#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, sys, io, os, platform
import tempfile
import subprocess
from glob import glob

from lib._version import __version__
from lib.stacked_tokenizer import StackedTokenizer
from lib.order_meta_tag import reorder
from lib.ekthetic_para import ekthetic_to_para
from lib.tt2conll import conllize
from lib.depedit import DepEdit
from lib.binarize_tags import binarize
from lib.lang import lookup_lang
from lib.harvest_tt_sgml import harvest_tt
from lib.mwe import tag_mwes

# Import pickled classes for RFTokenizer
from lib.tokenize_rf import MultiColumnLabelEncoder, DataFrameSelector, lambda_underscore

PY3 = sys.version_info[0] > 2

if PY3:
	from builtins import type

inp = input if PY3 else raw_input

script_dir = os.path.dirname(os.path.realpath(__file__))
lib_dir = script_dir + os.sep + "lib" + os.sep
bin_dir = script_dir + os.sep + "bin" + os.sep
data_dir = script_dir + os.sep + "data" + os.sep
parser_path = bin_dir + "maltparser-1.8" + os.sep
tt_path = bin_dir + "TreeTagger" + os.sep + "bin" + os.sep


def log_tasks(opts):
	sys.stderr.write("\nRunning standard tasks:\n" +"="*20 + "\n")
	if opts.unary:
		sys.stderr.write("o Binarize unary XML milestone tags\n")
	if opts.para:
		sys.stderr.write("o Paragraph detection\n")
	if opts.meta:
		sys.stderr.write("o Metadata insertion\n")
	if not opts.no_tok and not opts.parse_only and not opts.merge_parse:
		sys.stderr.write("o Tokenization\n")
	if opts.norm:
		sys.stderr.write("o Normalization\n")
	if opts.tag:
		sys.stderr.write("o POS tagging\n")
	if opts.lemma:
		sys.stderr.write("o Lemmatization\n")
	if opts.etym:
		sys.stderr.write("o Language of origin detection\n")
	if opts.multiword:
		sys.stderr.write("o Multiword expression recognition\n")
	if opts.sent is not None:
		sys.stderr.write("o Splitting sentences based on tag: "+opts.sent+"\n")
	if opts.parse or opts.parse_only or opts.merge_parse:
		sys.stderr.write("o Dependency parsing\n")

	special_tasks = []
	if opts.space:
		special_tasks.append("o Space out punctuation")
	if opts.merge_parse:
		special_tasks.append("o Merge parse into SGML file")
	if opts.para:
		special_tasks.append('o Add paragraphs based on <hi rend="ekthetic">')
	if opts.parse_only:
		special_tasks.append("o Parse to CoNLL file")
	if len(special_tasks) > 0:
		sys.stderr.write("\nRunning special tasks:\n" + "=" * 20 + "\n")
		sys.stderr.write("\n".join(special_tasks) + "\n")

	sys.stderr.write("\n")


def groupify(output,anno):
	groups = ""
	current_group = ""
	for line in output.split("\n"):
		if " "+anno+"=" in line:
			current_group += re.search(anno + r'="([^"]*)"',line).group(1)
		if line.startswith("</") and "_group" in line:
			groups += current_group +"\n"
			current_group = ""

	return groups


def remove_nesting_attr(data, nester, nested, attr="xml:lang"):
	"""
	Removes attribute on nesting element if a nested element includes it

	:param data: SGML input
	:param nester: nesting tag, e.g. "norm"
	:param nested: nested tag, e.g. "morph"
	:param attr: attribute, e.g. "lang"
	:return: cleaned SGML
	"""

	if attr not in data:
		return data
	flagged = []
	in_attr_nester = False
	last_nester = -1
	lines = data.split("\n")
	for i, line in enumerate(lines):
		if nester + "=" in line and attr+"=" in line:
			in_attr_nester = True
			last_nester = i
		if "</" + nester + ">" in line:
			in_attr_nester = False
		if nested in line and attr+"=" in line and in_attr_nester and last_nester > -1:
			flagged.append(last_nester)
			in_attr_nester = False
	for i in flagged:
		lines[i] = re.sub(' '+attr+'="[^"]+"','',lines[i])
	return "\n".join(lines)


def tok_from_norm(data):
	"""
	Takes TT-SGML, extracts norm attribute, and replaces existing tokens with norm values while retaining SGML tags.
	Used to feed parser norms while retaining SGML sentence separators.

	:param data: TTSGML with <norm norm=...> and raw tokens to replace
	:return: TTSGML with tags preserved and tokens replace by norm attribute values
	"""

	outdata = []
	norm = ""
	for line in data.replace("\r","").split("\n"):
		if line.startswith("<"):
			m = re.search(r'norm="([^"]*)"',line)
			if m is not None:
				norm = m.group(1)
			outdata.append(line)
		else:
			if norm != "":
				outdata.append(norm)
				norm=""
	return "\n".join(outdata) + "\n"


def read_attributes(input,attribute_name):
	out_stream =""
	for line in input.split('\n'):
		if attribute_name + '="' in line:
			m = re.search(attribute_name+r'="([^"]*)"',line)
			if m is None:
				print("ERR: cant find " + attribute_name + " in line: " + line)
				attribute_value = ""
			else:
				attribute_value = m.group(1)
			if len(attribute_value)==0:
				attribute_value = "_warn:empty_"+attribute_name+"_"
			out_stream += attribute_value +"\n"
	return out_stream


def merge_into_tag(tag_to_kill, tag_to_merge_into,stream):
	vals = []
	cleaned_stream = ""
	for line in stream.split("\n"):
		if " "+tag_to_kill + "=" in line:
			val = re.search(" " + tag_to_kill+'="([^"]*)"',line).group(1)
			vals.append(val)
		elif "</" + tag_to_kill + ">" in line:
			pass
		else:
			cleaned_stream += line + "\n"
	injected = inject(tag_to_kill,"\n".join(vals).strip(),tag_to_merge_into,cleaned_stream)
	return injected


def exec_via_temp(input_text, command_params, workdir=""):
	temp = tempfile.NamedTemporaryFile(delete=False)
	exec_out = ""
	try:
		if PY3:
			temp.write(input_text.encode("utf8"))
		else:
			temp.write(input_text)
		temp.close()

		command_params = [x if x != 'tempfilename' else temp.name for x in command_params]
		if workdir == "":
			proc = subprocess.Popen(command_params, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
			(stdout, stderr) = proc.communicate()
		else:
			proc = subprocess.Popen(command_params, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,cwd=workdir)
			(stdout, stderr) = proc.communicate()

		exec_out = stdout
	except Exception as e:
		print(e)
	finally:
		os.remove(temp.name)
		if PY3:
			exec_out = exec_out.decode("utf8")
		return exec_out


def get_origs(data):
	"""
	Harvests orig from plain tokens (non-tag lines of TT SGML), grouped by norm spans

	:param data: TT SGML with unnormalized tokens in non-tag lines and <norm.. tags indicating norm/orig borders
	:return: string containing one reconstituted orig unit per line
	"""

	origs = []
	current = ""
	for line in data.split("\n"):
		if "</norm>" in line:
			origs.append(current)
			current = ""
		if not line.startswith("<"):  # Token line
			current += line

	return "\n".join(origs)


def inject(attribute_name, contents, at_attribute,into_stream,replace=True):
	"""
	Inject new attributes and values into a specified SGML element in TT SGML format

	:param attribute_name: name of the attribute to insert
	:param contents: string, one value per line to insert as attribute values
	:param at_attribute: attribute in target element to insert this attribute before (can be same attribute name, replace in place)
	:param into_stream: TT SGML string with elements to add attributes to
	:param replace: boolean, whether to replace existing values of attribute_name when already present
	:return: TT SGML with added attributes
	"""
	insertions = contents.split('\n')
	injected = ""
	i=0
	for line in into_stream.split("\n"):
		if at_attribute + "=" in line:
			if i >= len(insertions):
				raise Exception("Error out of bounds at element " + str(i) + " in document beginning " + into_stream[:1000])
			if len(insertions[i])>0:
				if at_attribute == attribute_name:  # Replace old value of attribute with new one
					line = re.sub(attribute_name+'="[^"]*"',attribute_name+'="'+insertions[i]+'"',line)
				else:  # Place before specific at_attribute
					if replace or " " + attribute_name + "=" not in line:
						line = re.sub(at_attribute+"=",attribute_name+'="'+insertions[i]+'" '+at_attribute+"=",line)
			i += 1
		injected += line + "\n"
	return injected


def extract_conll(conll_string):
	conll_string = conll_string.replace("\r","").strip()
	sentences = conll_string.split("\n\n")
	ids = ""
	funcs = ""
	parents = ""
	id_counter = 0
	offset = 0
	for sentence in sentences:
		tokens = sentence.split("\n")
		for token in tokens:
			if "\t" in token:
				id_counter +=1
				ids += "u"+ str(id_counter) + "\n"
				cols = token.split("\t")
				funcs += cols[7].replace("ROOT","root") +"\n"
				if cols[6] == "0":
					parents += "#u0\n"
				else:
					parents += "#u" + str(int(cols[6])+offset)+"\n"
		offset = id_counter
	return ids, funcs, parents


def space_punct(input_text):
	punct = set(["·",".","·","ⲵ",",",":",";","ʼ","„","“","{","}"])
	if not PY3:
		punct = set([unicode(p) for p in punct])
	outstr = ""
	textmode = True
	for c in input_text:
		if c == "<":
			textmode = False
		if c in punct and textmode:
			outstr = "".join([outstr," " + c + " "])
		else:
			outstr = "".join([outstr,c])
		if c == ">":
			textmode = True
	outstr = re.sub(" +", " ", outstr)  # Kill double spaces
	return outstr


def inject_tags(in_sgml,insertion_specs,around_tag="norm",inserted_tag="multiword"):
	"""

	:param in_sgml: input SGML stream including tags to surround with new tags
	:param insertion_specs: list of triples (start, end, value)
	:param around_tag: tag of span to surround by insertion
	:return: modified SGML stream
	"""
	if len(insertion_specs) == 0:
		return in_sgml

	counter = -1
	next_insert = insertion_specs[0]
	insertion_counter = 0
	outlines = []
	for line in in_sgml.split("\n"):
		if line.startswith("<" + around_tag + " "):
			counter += 1
			if next_insert[0] == counter:  # beginning of a span
				outlines.append("<" + inserted_tag + " " + inserted_tag + '="' + next_insert[2] + '">')
		outlines.append(line)
		if line.startswith("</" + around_tag + ">"):
			if next_insert[1] == counter:  # end of a span
				outlines.append("</" + inserted_tag + ">")
				insertion_counter += 1
				if len(insertion_specs) > insertion_counter:
					next_insert = insertion_specs[insertion_counter]

	return "\n".join(outlines)


def check_requirements():
	tt_OK = True
	malt_OK = True
	tt = "tree-tagger"
	if platform.system() == "Windows":
		tt+=".exe"
	if not os.path.exists(tt_path + tt):
		sys.stderr.write("! TreeTagger not found at ./bin/\n")
		tt_OK = False
	if not os.path.exists(parser_path+"maltparser-1.8.jar"):
		sys.stderr.write("! Malt Parser 1.8 not found at ./bin/\n")
		malt_OK = False

	return tt_OK, malt_OK


def download_requirements(tt_ok=True, malt_ok=True):
	import requests, zipfile, shutil, tarfile
	if not PY3:
		import StringIO
	urls = []
	if not malt_ok:
		urls.append("http://maltparser.org/dist/maltparser-1.8.tar.gz")
	if not tt_ok:
		if platform.system() == "Windows":
			u = "http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/tree-tagger-windows-3.2.1.zip"
		elif platform.system() == "Darwin":
			u = "http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/tree-tagger-MacOSX-3.2.tar.gz"
		else:
			if "Red Hat Enterprise" in platform.linux_distribution()[0] and platform.linux_distribution()[1].startswith("6."):
				# Use older kernel version of TreeTagger for RHEL 6
				u = "http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/tree-tagger-linux-3.2-old5.tar.gz"
			else:
				u = "http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/tree-tagger-linux-3.2.1.tar.gz"
		if platform.system() != "Windows":  # Create TreeTagger subdirectory
			os.makedirs(bin_dir + "TreeTagger")
		urls.append(u)
	for u in urls:
		sys.stderr.write("o Downloading from " + u + "\n")
		r = requests.get(u, stream=True)
		if PY3:
			file_contents = io.BytesIO(r.content)
		else:
			file_contents = StringIO.StringIO(r.content)
		if u.endswith("zip"):
			z = zipfile.ZipFile(file_contents)
		else:
			z = tarfile.open(fileobj=file_contents, mode="r:gz")
		os_suf = ""
		if "tree" in u and platform.system() != "Windows":
			os_suf = "TreeTagger" + os.sep
		z.extractall(path=bin_dir + os_suf)
	shutil.copyfile(bin_dir+"coptic.mco",bin_dir+"maltparser-1.8" + os.sep + "coptic.mco")
	shutil.copyfile(bin_dir+"coptic_fine.par",bin_dir+"TreeTagger" + os.sep + "bin" + os.sep + "coptic_fine.par")


def nlp_coptic(input_data, lb=False, parse_only=False, do_tok=True, do_norm=True, do_mwe=True, do_tag=True, do_lemma=True, do_lang=True,
			   do_milestone=True, do_parse=True, sgml_mode="sgml", tok_mode="auto", old_tokenizer=False, sent_tag=None,
			   preloaded=None, pos_spans=False, merge_parse=False):

	data = input_data.replace("\t","")
	data = data.replace("\r","")

	if preloaded is not None:
		stk = preloaded
	else:
		stk = StackedTokenizer(pipes=sgml_mode != "sgml", lines=lb, tokenized=tok_mode=="from_pipes")

	if do_milestone:
		data = binarize(data)

	if do_tok:
		if old_tokenizer:
			tokenize = ['perl', lib_dir + 'tokenize_coptic.pl', '-n']
			if lb:
				tokenize.append('-l')
			if sgml_mode == "pipes":
				tokenize.append('-p')
			if tok_mode == "from_pipes":
				tokenize.append('-t')
			tokenize += ['-d', data_dir + 'copt_lex.tab', '-s', data_dir + 'segmentation_table.tab', '-m', data_dir + 'morph_table.tab', 'tempfilename']
			tokenized = exec_via_temp(data,tokenize)
			tokenized = tokenized.replace('\r','').strip()
			tokenized = re.sub(r'_$','',tokenized)
		else:
			tokenized = stk.analyze(data)

		if not lb and sgml_mode == "pipes":
			tokenized = tokenized.replace("\n","")
		if sgml_mode == "pipes":
			return tokenized
	else:
		tokenized = data
		if sgml_mode == "sgml" and "norm=" not in tokenized:
			# Assume raw one token per line, wrap everything in norm tags
			tok_lines = []
			for line in tokenized.split("\n"):
				if not line.startswith("<"):  # Leave XML tags alone
					line = '<norm_group norm_group="' + line + '">\n<norm norm="'+ line +'">\n' + line + '\n</norm>\n</norm_group>'
				tok_lines.append(line)
			tokenized = "\n".join(tok_lines)

	tokenized = tokenized.replace('\r','').strip()
	output = tokenized
	norms = read_attributes(tokenized,"norm")

	if do_norm:
		from lib.auto_norm import normalize
		norms = normalize(norms,table_file=data_dir + "norm_table.tab")
		output = inject("norm", norms, "norm", output)

	if parse_only or merge_parse:
		if not do_tag and (parse_only or merge_parse):
			if not "\t" in input_data and not 'pos="' in input_data:
				sys.stderr.write("! You selected parsing without tagging (-t) and your data format appears to contain no POS tag column.\n")
				resp = inp("! Would you like to add POS tagging to the job profile? [Y]es/[N]o/[A]bort ")
				if resp.lower() == "y":
					do_tag = True
				elif resp.lower() == "a":
					sys.exit(0)
		if do_tag:
			tag = [tt_path+'tree-tagger', tt_path+'coptic_fine.par', '-token','-lemma','-no-unknown', '-sgml' ,'tempfilename'] #no -token
			tagged = exec_via_temp(norms,tag)
			tagged = re.sub('\r','',tagged)
		else:  # Assume data is already tagged, in TT SGML format
			if pos_spans:
				tagged = harvest_tt(input_data, keep_sgml=True)
			else:
				tagged = input_data
				if PY3:
					tagged = input_data.encode("utf8")  # Handle non-UTF-8 when calling TT from subprocess in Python 3
		conllized = conllize(tagged,tag="PUNCT",element=sent_tag, no_zero=True)  # NB element is present it supercedes the POS tag
		deped = DepEdit(io.open(data_dir + "add_ud_and_flat_morph.ini",encoding="utf8"),options=type('', (), {"quiet":True})())
		depedited = deped.run_depedit(conllized.split("\n"))
		parse_coptic = ['java','-mx512m','-jar',"maltparser-1.8.jar",'-c','coptic','-i','tempfilename','-m','parse']
		parsed = exec_via_temp(depedited,parse_coptic,parser_path)
		deped = DepEdit(io.open(data_dir + "parser_postprocess_nodom.ini",encoding="utf8"),options=type('', (), {"quiet":True})())
		depedited = deped.run_depedit(parsed.split("\n"))
		if parse_only:  # Output parse in conll format
			return depedited
		elif merge_parse:  # Insert parse into input SGML as attributes of <norm>
			if "norm=" not in input_data:
				sys.stderr.write('ERR: --merge_parse was selected but no <norm norm=".."> tags found in input\n')
				sys.exit(0)
			if sgml_mode == "conllu":
				return depedited
			ids, funcs, parents = extract_conll(depedited.strip())
			output = inject("xml:id", ids, "norm", input_data)
			output = inject("func", funcs, "norm", output)
			output = inject("head", parents, "norm", output)
			output = output.replace(' head="#u0"', "")
			output = merge_into_tag("pos", "norm", output)
			output = merge_into_tag("lemma", "norm", output)
			return output

	elif not do_parse:
		tag = [tt_path + 'tree-tagger', tt_path+'coptic_fine.par', '-lemma','-no-unknown', '-sgml' ,'tempfilename'] #no -token
		tagged = exec_via_temp(norms,tag)
		tagged = re.sub('\r','',tagged)
	if do_parse:
		tag = [tt_path + 'tree-tagger', tt_path+'coptic_fine.par', '-token','-lemma','-no-unknown', '-sgml' ,'tempfilename'] #no -token
		if sent_tag is None:
			tagged = exec_via_temp(norms,tag)
		else:
			norm_with_sgml = tok_from_norm(output)
			tagged = exec_via_temp(norm_with_sgml,tag)
		tagged = re.sub('\r','',tagged)
		conllized = conllize(tagged, tag="PUNCT", element=sent_tag, no_zero=True)
		deped = DepEdit(io.open(data_dir + "add_ud_and_flat_morph.ini",encoding="utf8"),options=type('', (), {"quiet":True})())
		depedited = deped.run_depedit(conllized.split("\n"))
		parse_coptic = ['java','-mx1g','-jar',"maltparser-1.8.jar",'-c','coptic','-i','tempfilename','-m','parse']
		parsed = exec_via_temp(depedited,parse_coptic,parser_path)
		deped = DepEdit(io.open(data_dir + "parser_postprocess_nodom.ini",encoding="utf8"),options=type('', (), {"quiet":True})())
		depedited = deped.run_depedit(parsed.split("\n"))

		ids, funcs, parents = extract_conll(depedited)
		tagged = re.sub(r"(^|\n)[^\t]+\t",r"\1",tagged)
		if sent_tag is not None:
			tagged = re.sub(r"^<[^>]*>","",tagged)

	lemmas = re.sub('^[^\t]+\t','',tagged)
	lemmas = re.sub('\n[^\t]+\t','\n',lemmas)
	tagged = re.sub('(\t[^\t]+\n)','\n',tagged)
	langed = lookup_lang(norms, lexicon=data_dir + "lang_lexicon.tab")

	if do_parse:
		output = inject("xml:id",ids,"norm",output)
	if do_tag:
		output = inject("pos",tagged,"norm",output)
	if do_lemma:
		output = inject("lemma",lemmas,"norm",output)
	if do_mwe:
		mwe_positions = tag_mwes(norms.split('\n'),lemmas.split('\n'))
		output = inject_tags(output, mwe_positions)
	if do_lang:
		output = inject("xml:lang",langed,"norm",output)
		if "morph" in tokenized:
			morphs = read_attributes(tokenized, "morph")
			if len(morphs) > 0:
				# langed_morphs = exec_via_temp(morphs,lang).replace("\r","")
				langed_morphs = lookup_lang(morphs,lexicon=data_dir+"lang_lexicon.tab")
				output = inject("xml:lang", langed_morphs, "morph", output)
			# Make sure no foreign language norms also contain foreign language morphs (morph has priority over norm)
			output = remove_nesting_attr(output,"norm","morph","xml:lang")
	if do_parse:
		output = inject("func",funcs,"norm",output)
		output = inject("head",parents,"norm",output)
		output = output.replace(' head="#u0"',"")  # Remove head attribute for root tokens in dependency tree

	if do_norm and "norm=" in output:
		groups = groupify(output,"norm")
		output = inject("norm_group",groups,"norm_group",output)

		# Add orig from tokens based on norm spans
		origs = get_origs(output)
		output = inject("orig",origs,"norm",output)
		orig_groups = groupify(output, "orig")
		if "orig_group=" in output:
			# Replace existing orig groups in output with newly harvested orig content
			output = inject("orig_group",orig_groups,"orig_group",output)
		else:
			# Add orig_group attribute since not yet present
			output = inject("orig_group",orig_groups,"norm_group",output)
	else:
		if "orig_group=" in tokenized:  # There are already orig_group attrs and we're not normalizing
			orig_groups = read_attributes(tokenized, "orig_group")
			origs = get_origs(tokenized)
			output = inject("orig", origs, "orig", output)
			output = inject("orig_group", orig_groups, "orig_group", output)
		elif "orig=" in tokenized:  # Need to reconstitute
			origs = get_origs(tokenized)
			orig_groups = groupify(tokenized, "orig")
			output = inject("orig", origs, "orig", output)
			output = inject("orig_group", orig_groups, "orig_group", output)

	return output.strip() + "\n"


if __name__ == "__main__":

	if sys.version_info[0] == 2 and sys.version_info[1] < 7:
		sys.stderr.write("Python versions below 2.7 are not supported.\n")
		sys.stderr.write("Your Python version:\n")
		sys.stderr.write(".".join([str(v) for v in sys.version_info[:3]]) + "\n")
		sys.exit(0)

	from argparse import ArgumentParser, RawDescriptionHelpFormatter

	parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
	parser.prog = "Coptic NLP Pipeline"
	parser.usage = "python coptic_nlp.py [OPTIONS] files"
	parser.epilog = """Example usage:
--------------
Add norm, lemma, parse, tag, unary tags, find multiword expressions and do language recognition:
> python coptic_nlp.py -penmult infile.txt        

Just tokenize a file using pipes and dashes:
> python coptic_nlp.py -o pipes infile.txt       

Tokenize with pipes and mark up line breaks:
> python coptic_nlp.py -b -o pipes infile.txt

Normalize, tag, lemmatize, find multiword expressions and parse, splitting sentences by <verse> tags:
> python coptic_nlp.py -pnltm -s verse infile.txt       

Add full analyses to a whole directory of *.xml files, output to a specified directory:    
> python coptic_nlp.py -penmult --dirout /home/cop/out/ *.xml

Parse a tagged SGML file into CoNLL tabular format for treebanking, use translation tag to recognize sentences:
> python coptic_nlp.py --no_tok --parse_only --pos_spans -s translation infile.tt

Merge a parse into a tagged SGML file's <norm> tags, use translation tag to recognize sentences:
> python coptic_nlp.py --merge_parse --pos_spans -s translation infile.tt
"""
	parser.add_argument("files", help="File name or pattern of files to process (e.g. *.txt)")

	g1 = parser.add_argument_group("standard module options")
	g1.add_argument("-u","--unary", action="store_true", help='Binarize unary XML milestone tags')
	g1.add_argument("-t","--tag", action="store_true", help='Do POS tagging')
	g1.add_argument("-l","--lemma", action="store_true", help='Do lemmatization')
	g1.add_argument("-n","--norm", action="store_true", help='Do normalization')
	g1.add_argument("-m","--multiword", action="store_true", help='Tag multiword expressions')
	g1.add_argument("-b","--breaklines", action="store_true", help='Add line tags at line breaks')
	g1.add_argument("-p","--parse", action="store_true", help='Parse with dependency parser')
	g1.add_argument("-e","--etym", action="store_true", help='Add etymolgical language of origin for loan words')
	g1.add_argument("-s","--sent", action="store", help='XML tag to split sentences, e.g. verse for <verse ..> (otherwise PUNCT tag is used to split sentences)')
	g1.add_argument("-o","--outmode", action="store", choices=["pipes","sgml","conllu"], default="sgml", help='Output SGML, conllu or tokenize with pipes')

	g2 = parser.add_argument_group("less common options")
	g2.add_argument("-f","--finitestate", action="store_true", help='Use old finite-state tokenizer (less accurate)')
	g2.add_argument("-q","--quiet", action="store_true", help='Suppress verbose messages')
	g2.add_argument("-x","--extension", action="store", default=None, help='Extension for SGML mode output files (default: tt)')
	g2.add_argument("--stdout", action="store_true", help='Print output to stdout, do not create output file')
	g2.add_argument("--para", action="store_true", help='Add <p> tags if <hi rend="ekthetic"> is present')
	g2.add_argument("--space", action="store_true", help='Add spaces around punctuation')
	g2.add_argument("--from_pipes", action="store_true", help='Tokenization is indicated in input via pipes')
	g2.add_argument("--dirout", action="store", default=".", help='Optional output directory (default: this dir)')
	g2.add_argument("--meta", action="store", default=None, help='Add fixed meta data string read from this file name')
	g2.add_argument("--parse_only", action="store_true", help='Only add a parse to an existing tagged SGML input')
	g2.add_argument("--no_tok", action="store_true", help='Do not tokenize at all, input is one token per line')
	g2.add_argument("--pos_spans", action="store_true", help='Harvest POS tags and lemmas from SGML spans')
	g2.add_argument("--merge_parse", action="store_true", help='Merge/add a parse into a ready SGML file')
	g2.add_argument("--version", action="store_true", help='Print version number and quit')

	if "--version" in sys.argv:
		sys.stdout.write("Coptic NLP Pipeline V" + __version__)
		sys.exit(1)

	opts = parser.parse_args()
	old_tokenizer = True if opts.finitestate else False
	dotok = False if opts.no_tok or opts.merge_parse else True

	if not opts.quiet:
		from lib import timing

	add_fixed_meta = ""
	if opts.meta is not None:
		add_fixed_meta = io.open(opts.meta, encoding="utf8").read()

	files = glob(opts.files)

	if not opts.quiet:
		log_tasks(opts)

	if dotok and not old_tokenizer:
		# Pre-load stacked tokenizer for entire batch
		stk = StackedTokenizer(pipes=opts.outmode == "pipes", lines=opts.breaklines, tokenized=opts.from_pipes)
	else:
		stk = None

	# Check if TreeTagger and Malt Parser are available
	tt_OK, malt_OK = check_requirements()
	if (opts.tag and not tt_OK) or ((opts.parse or opts.parse_only or opts.merge_parse) and not malt_OK):
		sys.stderr.write("! You are missing required software:\n")
		if opts.tag and not tt_OK:
			sys.stderr.write(" - Tagging is specified but TreeTagger is not installed\n")
		if (opts.parse or opts.parse_only or opts.merge_parse) and not malt_OK:
			sys.stderr.write(" - Parsing is specified but Malt Parser 1.8 is not installed\n")
		response = inp("Attempt to download missing software? [Y/N]\n")
		if response.upper().strip() == "Y":
			download_requirements(tt_OK,malt_OK)
		else:
			sys.stderr.write("Aborting\n")
			sys.exit(0)

	for infile in files:
		base = os.path.basename(infile)
		if opts.extension is None:  # Auto select extension
			if opts.parse_only:
				opts.extension = "conllu"
			else:
				opts.extension = "tt"
		if opts.outmode == "sgml":
			if infile.endswith("." + opts.extension):
				outfile = base.replace("." + opts.extension,".out." + opts.extension)
			elif len(infile) > 4 and infile[-4] == ".":
				outfile = base[:-4] + "." + opts.extension
			else:
				outfile = base + "." + opts.extension
		elif opts.outmode == "conllu":
			opts.extension = "conllu"
		else:
			outfile = base + ".out.txt"

		if not opts.quiet:
			sys.stderr.write("Processing " + base + "\n")

		input_text = io.open(infile,encoding="utf8").read()
		if opts.space:
			input_text = space_punct(input_text)

		if opts.para:
			input_text = ekthetic_to_para(input_text)

		if opts.merge_parse and not opts.pos_spans:
			sys.stderr.write("o --merge_parse was selected; turning on --pos_spans option")
			opts.pos_spans = True

		processed = nlp_coptic(input_text, lb=opts.breaklines, parse_only=opts.parse_only, do_tok=dotok,
							   do_norm=opts.norm, do_mwe=opts.multiword, do_tag=opts.tag, do_lemma=opts.lemma,
							   do_lang=opts.etym, do_milestone=opts.unary, do_parse=opts.parse, sgml_mode=opts.outmode,
							   tok_mode="auto", old_tokenizer=old_tokenizer, sent_tag=opts.sent, preloaded=stk,
							   pos_spans=opts.pos_spans, merge_parse=opts.merge_parse)

		if opts.outmode == "sgml":
			processed = reorder(processed.strip().split("\n"),add_fixed_meta=add_fixed_meta)
			processed = processed.replace("xml:lang","lang")

		if len(files) > 1:
			with io.open(opts.dirout + os.sep + outfile, 'w', encoding="utf8", newline="\n") as f:
				if not PY3:
					processed = unicode(processed)
				f.write((processed.strip() + "\n"))
		else:  # Single file, print to stdout
			if PY3:
				sys.stdout.buffer.write(processed.encode("utf8"))
			else:
				print(processed.encode("utf8"))

	fileword = " files\n\n" if len(files) > 1 else " file\n\n"
	sys.stderr.write("\nFinished processing " + str(len(files)) + fileword)
