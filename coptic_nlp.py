#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, sys, io, os, platform
import tempfile
import subprocess
from glob import glob

from lib._version import __version__
from lib.stacked_tokenizer import StackedTokenizer
from lib.order_meta_tag import reorder
from lib.reorder_sgml import reorder as reorder_sgml
from lib.ekthetic_para import ekthetic_to_para
from lib.tt2conll import conllize
from lib.depedit import DepEdit
from lib.binarize_tags import binarize
from lib.lang import lookup_lang
from lib.harvest_tt_sgml import harvest_tt
from lib.mwe import tag_mwes
from lib.marmot import tag_marmot
from lib.flair_pos_tagger import FlairTagger
from lib.lemmatize import Lemmatizer
from lib.heads import assign_entity_heads

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
ud_coptic_path = script_dir + os.sep + "UD_Coptic-Scriptorium" + os.sep  # Optional path to UD_Coptic-Scriptorium - use to cache gold parses

from diaparser.parsers.parser import Parser as NeuralParser
neural_model = script_dir + os.sep + "lib" + os.sep + "cop.diaparser"
from lib.quiet import suppress_stdout_stderr  # Context to suppress stderr messages from imported libraries

# Global cache of gold syntax trees, if UD_Coptic-Scriptorium data is available
gold_trees = {}

# Place holder for entity linking module
identifier = None

def get_gold_trees():
	def conll2mapping(conllu):
		out_dict = {}
		sents = conllu.strip().replace("\r","").split("\n\n")
		for sent in sents:
			out_sent = []
			tokens = []
			for line in sent.split("\n"):
				if "\t" in line:
					fields = line.split("\t")
					if "-" not in fields[0]:
						tokens.append(fields[1])
						fields[5], fields[-2], fields[-1] = "_", "_", "_"  # Kill MISC, FEATS
						fields[3] = fields[4]  # Kill UPOS
						out_sent.append("\t".join(fields))
			out_dict[" ".join(tokens)] = "\n".join(out_sent)
		return out_dict

	global ud_coptic_path
	global gold_trees
	partition_files = ["train","test","dev"]
	if os.path.exists(ud_coptic_path + 'cop_scriptorium-ud-train.conllu'):
		partition_files = [ud_coptic_path + "cop_scriptorium-ud-" + f + ".conllu" for f in partition_files]
		for f in partition_files:
			gold_trees.update(conll2mapping(io.open(f,encoding="utf8").read()))


def replace_trees(conllu, gold_trees):
	sents = conllu.strip().replace("\r", "").split("\n\n")
	output = []
	for sent in sents:
		tokens = []
		for line in sent.split("\n"):
			if "\t" in line:
				fields = line.split("\t")
				if "-" not in fields[0]:
					tokens.append(fields[1])
		plain = " ".join(tokens)
		if plain in gold_trees:
			output.append(gold_trees[plain])
		else:
			output.append(sent)

	return "\n\n".join(output) + "\n\n"


# Global lookup lemmatizer
lemmatizer = Lemmatizer(data_dir + "copt_lemma_lex.tab", no_unknown=True)
flair_tagger = None

def log_tasks(opts):
	sys.stderr.write("\nRunning standard tasks:\n" +"="*20 + "\n")
	if opts.unary:
		sys.stderr.write("o Binarize unary XML milestone tags\n")
	if opts.para:
		sys.stderr.write("o Paragraph detection\n")
	if opts.meta:
		sys.stderr.write("o Metadata insertion\n")
	if not opts.no_tok and not opts.parse_only and not opts.merge_parse:
		if opts.from_pipes:
			sys.stderr.write("o Tokenization (from pipes)\n")
		else:
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
	if opts.recognize_entities:
		sys.stderr.write("o Entity recognition\n")
	if opts.identities:
		sys.stderr.write("o Wikification\n")

	special_tasks = []
	if opts.space:
		special_tasks.append("o Space out punctuation")
	if opts.detokenize > 0:
		if opts.detokenize == 2:
			special_tasks.append("o Detokenization (a.k.a. 'Laytonization') - aggressive")
		elif opts.detokenize == 3:
			special_tasks.append("o Detokenization (a.k.a. 'Laytonization') - smart")
		else:
			special_tasks.append("o Detokenization (a.k.a. 'Laytonization') - conservative")
	if opts.segment_merged:
		special_tasks.append("o Insert boundary between merged groups")
	if opts.breaklines:
		special_tasks.append("o Add line tags to preserve line breaks")
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
			groups += current_group + "\n"
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
					if replace and ' ' + attribute_name + '=' in line:
						line = re.sub(' ' + attribute_name + '="[^"]*"','',line)  # Remove old value
					line = re.sub(at_attribute+"=",attribute_name+'="'+insertions[i]+'" '+at_attribute+"=",line)
			i += 1
		injected += line + "\n"
	return injected


def extract_conll(conll_string, mark_new_sent=True):
	conll_string = conll_string.replace("\r","").strip()
	sentences = conll_string.split("\n\n")
	ids = ""
	funcs = ""
	parents = ""
	id_counter = 0
	offset = 0
	new_sents = ""
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
				if cols[0] == "1" and mark_new_sent:
					new_sents += "true\n"
				else:
					new_sents += "false\n"
		offset = id_counter
	return ids, funcs, parents, new_sents


def parse2conllu(parser_output, tagged):
	output = []
	tags = [l.split("\t")[1] for l in tagged.split("\n") if "\t" in l]
	lemmas = [l.split("\t")[2] for l in tagged.split("\n") if "\t" in l]
	toknum = -1
	for sent in parser_output.sentences:
		tid = -1
		for position in sorted(list(sent.annotations.keys())):
			fields = sent.annotations[position]
			if "\t" in fields:
				toknum += 1
				tid += 1
				fields = fields.split("\t")
				fields[3] = fields[4] = tags[toknum]
				fields[2] = lemmas[toknum]
				fields[6] = str(sent.values[6][tid])
				fields[7] = sent.values[7][tid]
				fields = "\t".join(fields)
			output.append(fields)
		output.append("")
	return "\n".join(output)


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


def inject_with_nesting(in_sgml,insertion_specs,around_tag="norm",inserted_tag="entity"):
	"""
	Inject possibly nesting annotations around existing tags

	:param in_sgml: input SGML stream including tags to surround with new tags
	:param insertion_specs: list of triples (start, end, value), where start/end correspond to positions of around_tag
	:param around_tag: tag of span to surround by insertion
	:param inserted_tag: tag and attribute name to wrap inserted values in
	:return: modified SGML stream
	"""

	lines = in_sgml.split("\n")
	open_positions = [i for i in range(len(lines)) if lines[i].startswith("<" + around_tag+" ")]
	for insertion in insertion_specs[::-1]:  # Insert opening tags at desired indices in reverse
		lines.insert(open_positions[insertion[0]],'<'+inserted_tag+' '+inserted_tag+'="' + insertion[2] + '">')

	close_positions = [i for i in range(len(lines)) if lines[i] == "</" + around_tag + ">"]
	insertion_specs.sort(key=lambda x:x[1])  # Sort by closing index
	for insertion in insertion_specs[::-1]:  # Insert opening tags at desired indices in reverse
		lines.insert(close_positions[insertion[1]]+1,'</'+inserted_tag+'>')

	return "\n".join(lines)


def get_entity_offsets(sgml):
	lines = sgml.split("\n")
	started = []
	entities = []
	toknum = 0
	for line in lines:
		if 'entity="' in line:
			entity_type = re.search(r' entity="([^"]*)"',line).group(1)
			started.append((toknum,entity_type))
		elif '</referent>' in line:
			start, entity_type = started.pop()
			entities.append((start,toknum-1,entity_type))
		elif not line.startswith("<") and not line.endswith(">") and len(line)>0:  # Token
			toknum += 1

	return sorted(entities,key=lambda x: (x[0],-x[1]))


def analyze_entities(conll_parse,sgml_so_far,preloaded,outmode,do_identities=False,docname=None):
	if preloaded is None:
		preloaded = {"stk":None,"xrenner":None,"parser":None,"tagger":None}
	if preloaded["xrenner"] is None:
		from xrenner import Xrenner  # lib.
		xrenner = Xrenner(model=lib_dir + "cop.xrm")
		preloaded["xrenner"] = xrenner
	else:
		xrenner = preloaded["xrenner"]
	xrenner.docname = "_"

	# Make sure we don't have stale entity annotations in input
	sgml_so_far = re.sub(r'</?entity[^\n]+\n','',sgml_so_far)

	if outmode == "sgml":
		ents = xrenner.analyze(conll_parse, "sgml")  # "conll_sent")
		insertion_specs = get_entity_offsets(ents)  # Get [(start, end, entity_type),...]
		output = inject_with_nesting(sgml_so_far, insertion_specs, around_tag="norm", inserted_tag="entity")
		# Ensure entity nests norm
		output = reorder_sgml(output.strip(),priorities=["entity", "orig_group", "norm_group", "norm", "orig"])
		output = assign_entity_heads(output)
		if do_identities:
			identifier.read_words(output)
			output = identifier.predict_sgml(output, docname=docname)
		return output
	elif outmode == "conllu":
		ents = xrenner.analyze(conll_parse, "conll_sent")
		ents = ents.replace("\n\n", "\n").strip().split("\n")
		ents = [line.split("\t")[-1] for line in ents if "\t" in line]
		counter = 0
		out_conll = []
		for line in conll_parse.split("\n"):
			if "\t" in line:
				fields = line.split("\t")
				fields[-1] = ents[counter]
				line = "\t".join(fields)
				counter += 1
			out_conll.append(line)
		return "\n".join(out_conll)


def postag(indata, full_sgml, tagger="flair",notokens=False,sent=None,tabular=False,postprocess=True,preloaded=None):
	if tagger=="treetagger":
		tag = [tt_path + 'tree-tagger', tt_path+'coptic_fine.par', '-lemma','-no-unknown', '-sgml'] #no -token
		if not notokens:
			tag += ['-token']
		tag += ['tempfilename']
		tagged = exec_via_temp(indata,tag)
		if notokens:
			return tagged
	elif tagger=="marmot":
		tagged = tag_marmot(indata, sent=sent)
		tagged = lemmatizer.lemmatize(tagged)
	elif tagger=="flair":
		sentstr = "translation" if sent is None else sent
		tagged = preloaded["tagger"].predict(full_sgml, in_format="sgml", out_format="tt", sent=sentstr, as_text=True)
		tagged = lemmatizer.lemmatize(tagged)
	spl = [line.split("\t") for line in tagged.strip().split("\n")]
	words, tags, lemmas = zip(*spl)

	if postprocess:  # Replace implausible word+tag combinations
		tags = list(tags)
		tagtab = io.open(data_dir+"postprocess_tagger.tab", encoding="utf8").read().replace("\r", "").strip().split("\n")
		mapping = dict(((line.split("\t")[0], line.split("\t")[1]), line.split("\t")[2]) for line in tagtab)
		for i, word in enumerate(words):
			tag = tags[i]
			if (word, tag) in mapping:
				tags[i] = mapping[(word, tag)]
			elif (word, "*") in mapping:
				tags[i] = mapping[(word, "*")]

	if tabular and not notokens:
		return "\n".join([words[i]+"\t"+tags[i]+"\t"+lemmas[i] for i in range(len(tags))])
	elif notokens:
		return "\n".join([tags[i]+"\t"+lemmas[i] for i in range(len(tags))])
	tagged = inject("pos","\n".join(tags),"norm",indata)
	tagged = inject("lemma","\n".join(lemmas),"norm",tagged)
	tagged = re.sub('\r','',tagged)

	return tagged


def check_requirements(require_tt=False):
	marmot_OK = True
	tt_OK = True
	malt_OK = True
	foma_OK = True
	tt = "tree-tagger"
	if platform.system() == "Windows":
		tt+=".exe"
	if not os.path.exists(tt_path + tt) and require_tt:
		sys.stderr.write("! TreeTagger not found at ./bin/\n")
		tt_OK = False
	if not os.path.exists(parser_path+"maltparser-1.8.jar"):
		sys.stderr.write("! Malt Parser 1.8 not found at ./bin/\n")
		malt_OK = False
	if not os.path.exists(bin_dir+"marmot"+os.sep+"marmot.jar"):
		sys.stderr.write("! Marmot not found at ./bin/marmot/\n")
		marmot_OK = False
	if not (os.path.exists(bin_dir + "foma" + os.sep + "flookup") or os.path.exists(bin_dir + "foma" + os.sep + "flookup.exe")):
		sys.stderr.write("! Foma flookup not found at ./bin/foma/\n")
		foma_OK = False

	return tt_OK, malt_OK, foma_OK, marmot_OK


def download_requirements(tt_ok=True, malt_ok=True, foma_ok=True, marmot_ok=True, require_tt=False, require_malt=False):
	import requests, zipfile, shutil, tarfile
	if not PY3:
		import StringIO
	urls = []
	if not foma_ok:
		if platform.system() == "Windows":
			with zipfile.ZipFile(bin_dir+"foma"+os.sep+"foma_win.zip", 'r') as z:
				z.extractall(bin_dir+"foma"+os.sep)
		elif platform.system() == "Darwin":
			with zipfile.ZipFile(bin_dir+"foma"+os.sep+"foma_osx.zip", 'r') as z:
				z.extractall(bin_dir+"foma"+os.sep)
		else:  # Linux
			sys.stderr.write("! Need to compile foma on Linux and place flookup in bin/foma/\n! See bin/foma/README.md \n")
			sys.exit(0)
	if not marmot_ok:
		if not os.path.exists(bin_dir + "marmot"):
			os.makedirs(bin_dir + "marmot")
		marmot_base_url = "http://cistern.cis.lmu.de/marmot/bin/CURRENT/"
		marmot_current = requests.get(marmot_base_url).text
		files = re.findall(r'href="((?:marmot|trove)[^"]+jar)"',marmot_current)
		marmot_file = ""
		trove_file = ""
		for f in files:
			if f.startswith("marmot"):
				marmot_file = f
			elif f.startswith("trove"):
				trove_file = f
		urls.append(marmot_base_url + marmot_file)
		urls.append(marmot_base_url + trove_file)
	if not malt_ok and require_malt:
		urls.append("http://maltparser.org/dist/maltparser-1.8.tar.gz")
	if not tt_ok and require_tt:
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
		elif u.endswith("jar"):
			if "trove" in u:
				with open(bin_dir + "marmot" + os.sep + "trove.jar", 'wb') as f:
					f.write(r.content)
			elif "marmot" in u:
				with open(bin_dir + "marmot" + os.sep + "marmot.jar", 'wb') as f:
					f.write(r.content)
			continue
		else:
			z = tarfile.open(fileobj=file_contents, mode="r:gz")
		os_suf = ""
		if "tree" in u and platform.system() != "Windows":
			os_suf = "TreeTagger" + os.sep
		z.extractall(path=bin_dir + os_suf)
	if not malt_OK and require_malt:
		shutil.copyfile(bin_dir+"coptic.mco",bin_dir+"maltparser-1.8" + os.sep + "coptic.mco")
	if not tt_ok and require_tt:
		shutil.copyfile(bin_dir+"coptic_fine.par",bin_dir+"TreeTagger" + os.sep + "bin" + os.sep + "coptic_fine.par")


def nlp_coptic(input_data, lb=False, parse_only=False, do_tok=True, do_norm=True, do_mwe=True, do_tag=True, do_lemma=True, do_lang=True,
			   do_milestone=True, do_parse=True, sgml_mode="sgml", tok_mode="auto", old_tokenizer=False, sent_tag=None,
			   preloaded=None, pos_spans=False, merge_parse=False, detokenize=0, segment_merged=False, gold_parse="",
			   tagger="flair", parser="diaparser", do_entities=False, no_gold_parse=False, mark_new_sent=True, do_identities=False,
			   docname=None):

	if docname is not None:
		docname = docname.replace(".tt","").replace(".sgml","").replace(".xml","").replace(".txt","")

	if preloaded is None:
		with suppress_stdout_stderr():
			preloaded = {"stk":None,"xrenner":None,"parser":NeuralParser.load(neural_model),"tagger":FlairTagger()}

	with suppress_stdout_stderr():
		neural_parser = preloaded["parser"] if preloaded["parser"] is not None else NeuralParser.load(neural_model)
	data = input_data.replace("\t","")
	data = data.replace("\r","")

	if preloaded["stk"] is not None:
		stk = preloaded["stk"]
	else:
		stk = StackedTokenizer(pipes=sgml_mode != "sgml", lines=lb, tokenized=tok_mode=="from_pipes",
							   detok=detokenize, segment_merged=segment_merged, ambig=data_dir + "ambig.tab")

	if do_milestone:
		data = binarize(data)

	if do_entities and not do_parse and not parse_only and not merge_parse:
		do_parse = True

	if do_tok:
		if old_tokenizer:
			tokenize = ['perl', lib_dir + 'tokenize_coptic.pl', '-n']
			if lb:
				tokenize.append('-l')
			if sgml_mode == "pipes":
				tokenize.append('-p')
			if tok_mode == "from_pipes":
				tokenize.append('-t')
			tokenize += ['-d', data_dir + 'copt_lemma_lex.tab', '-s', data_dir + 'segmentation_table.tab', '-m', data_dir + 'morph_table.tab', 'tempfilename']
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
			if "\t" not in input_data and 'pos="' not in input_data:
				sys.stderr.write("! You selected parsing without tagging (-t) and your data format appears to contain no POS tag column.\n")
				resp = inp("! Would you like to add POS tagging to the job profile? [Y]es/[N]o/[A]bort ")
				if resp.lower() == "y":
					do_tag = True
				elif resp.lower() == "a":
					sys.exit(0)
		if do_tag and not pos_spans:
			tagged = postag(norms, output, tagger=tagger,sent=sent_tag, preloaded=preloaded)
		else:  # Assume data is already tagged, in TT SGML format
			if pos_spans:
				tagged = harvest_tt(input_data, keep_sgml=True)
			else:
				tagged = input_data
				if PY3:
					tagged = input_data.encode("utf8")  # Handle non-UTF-8 when calling TT from subprocess in Python 3
		if gold_parse == "":
			# NB if element is present for conllize it supercedes the POS tag for sentence splitting
			if parser != "malt":
				conllized = conllize(tagged, tag="PUNCT", element=sent_tag, no_zero=True, ten_cols=True)
				for_parser = []
				for s in conllized.strip().split("\n\n"):
					for_parser.append([l.split("\t")[1] for l in s.split("\n") if "\t" in l])
				parsed = neural_parser.predict(conllized.strip()+"\n\n")
				parsed = parse2conllu(parsed,tagged)
			else:
				conllized = conllize(tagged, tag="PUNCT", element=sent_tag, no_zero=True)
				deped = DepEdit(io.open(data_dir + "add_ud_and_flat_morph.ini",encoding="utf8"),options=type('', (), {"quiet":True, "kill":None})())
				depedited = deped.run_depedit(conllized.split("\n"))
				#depedited = conllized
				parse_coptic = ['java','-mx512m','-jar',"maltparser-1.8.jar",'-c','coptic','-i','tempfilename','-m','parse']
				if not os.path.exists(bin_dir+"maltparser-1.8" + os.sep + "coptic.mco"):
					sys.stderr.write("! can't find coptic.mco parser model in " + bin_dir+"maltparser-1.8" + os.sep + "coptic.mco")
					sys.exit(0)
				parsed = exec_via_temp(depedited,parse_coptic,parser_path)
			deped = DepEdit(io.open(data_dir + "postprocess_parser.ini",encoding="utf8"),options=type('', (), {"quiet":True, "kill":None})())
			depedited = deped.run_depedit(parsed.split("\n"))
			if len(gold_trees) == 0 and not no_gold_parse:
				get_gold_trees()
			if len(gold_trees) > 0:
				# Replace automatic parses with cached trees from UD_Coptic if available
				depedited = replace_trees(depedited, gold_trees)
		else:  # A cached gold parse has been specified by the user
			depedited = gold_parse
			norm_count = len(re.findall(r'(\n|^)[0-9]+\t',depedited))
			input_norms = input_data.count(" norm=")
			if norm_count != input_norms:
				dped = re.findall(r'(?:\n|^)[0-9]+\t([^\n\t]+)',depedited)
				nrms = re.findall(r' norm="([^"]*)"',input_data)
				for i, nrm in enumerate(nrms):
					if nrm != dped[i]:
						mismatch = nrm +"!="+dped[i] + " at " + str(i) + " after " + nrms[i-2] + " " +  nrms[i-1]
						break
				raise IOError("Mismatch in word count: " + str(norm_count) + " in gold parse but " + str(input_norms) + " in SGML file\nMismatch: "+ mismatch)
		if do_entities:
			if do_identities:
				sys.stderr.write("! ignoring Wikification task due to parser merge workflow")
			ents = analyze_entities(depedited, output, preloaded, sgml_mode, do_identities=False, docname=docname)
			if sgml_mode == "conllu":
				depedited = ents
			else:
				output = ents
		else:
			output = input_data

		if parse_only:  # Output parse in conll format
			return depedited
		elif merge_parse:  # Insert parse into input SGML as attributes of <norm>
			if "norm=" not in input_data:
				sys.stderr.write('ERR: --merge_parse was selected but no <norm norm=".."> tags found in input\n')
				sys.exit(0)
			if sgml_mode == "conllu":
				return depedited
			ids, funcs, parents, new_sents = extract_conll(depedited.strip(), mark_new_sent=mark_new_sent)
			output = inject("xml:id", ids, "norm", output)
			output = inject("func", funcs, "norm", output)
			output = inject("head", parents, "norm", output)
			output = inject("new_sent", new_sents, "norm", output)
			output = output.replace(' head="#u0"', "").replace(' new_sent="false"', "")
			output = merge_into_tag("pos", "norm", output)
			output = merge_into_tag("lemma", "norm", output)
			return output

	elif not do_parse:
		tagged = postag(norms,output,tagger=tagger,sent=sent_tag,notokens=True, preloaded=preloaded)
	if do_parse:
		if sent_tag is None:
			tagged = postag(norms,output,tagger=tagger,sent=sent_tag,tabular=True, preloaded=preloaded)
		else:
			norm_with_sgml = tok_from_norm(output)
			tagged = postag(norm_with_sgml,output,tagger=tagger,sent=sent_tag,tabular=False, preloaded=preloaded)
		if parser!="malt":
			conllized = conllize(tagged, tag="PUNCT", element=sent_tag, no_zero=True, ten_cols=True)
			for_parser = []
			for s in conllized.strip().split("\n\n"):
				for_parser.append([l.split("\t")[1] for l in s.split("\n") if "\t" in l])
			parsed = neural_parser.predict(for_parser)
			parsed = parse2conllu(parsed,tagged)
		else:
			conllized = conllize(tagged, tag="PUNCT", element=sent_tag, no_zero=True)
			if not os.path.exists(bin_dir + "maltparser-1.8" + os.sep + "coptic.mco"):
				sys.stderr.write(
					"! can't find coptic.mco parser model in " + bin_dir + "maltparser-1.8" + os.sep + "coptic.mco")
				sys.exit(0)
			deped = DepEdit(io.open(data_dir + "add_ud_and_flat_morph.ini", encoding="utf8"),
							options=type('', (), {"quiet": True, "kill": "supertoks"})())
			depedited = deped.run_depedit(conllized.split("\n"))
			# depedited = conllized
			parse_coptic = ['java','-mx1g','-jar',"maltparser-1.8.jar",'-c','coptic','-i','tempfilename','-m','parse']
			parsed = exec_via_temp(depedited,parse_coptic,parser_path)
		deped = DepEdit(io.open(data_dir + "postprocess_parser.ini",encoding="utf8"),options=type('', (), {"quiet":True,"kill":"supertoks"})())
		depedited = deped.run_depedit(parsed.split("\n"))
		if len(gold_trees) > 0:
			# Replace automatic parses with cached trees from UD_Coptic if available
			depedited = replace_trees(depedited, gold_trees)

		if sgml_mode == "conllu" and not do_entities:  # Return conllu parse and finish
			return depedited

		ids, funcs, parents, new_sents = extract_conll(depedited, mark_new_sent=mark_new_sent)
		tagged = re.sub(r"(^|\n)[^\t]+\t",r"\1",tagged)
		if sent_tag is not None:
			tagged = re.sub(r"^<[^>]*>","",tagged)

	if "\t" in tagged:
		lemmas = re.sub(r'^[^\t]+\t','',tagged)
		lemmas = re.sub(r'\n[^\t]+\t','\n',lemmas)
		tagged = re.sub(r'(\t[^\t]+(\n|$))','\n',tagged).strip()
	else:
		lemmas = read_attributes(tagged,"lemma")
		tagged = read_attributes(tagged, "pos")
	langed = lookup_lang(norms, lexicon=data_dir + "lang_lexicon.tab")

	if do_parse:
		output = inject("xml:id",ids,"norm",output)
	if do_tag:
		output = inject("pos",tagged,"norm",output)
	if do_lemma:
		output = inject("lemma",lemmas,"norm",output)
	if do_mwe:
		mwe_positions = tag_mwes(norms.split('\n'),lemmas.split('\n'))
		output = inject_with_nesting(output, mwe_positions, inserted_tag="multiword")
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
		output = inject("new_sent",new_sents,"norm",output)
		# Remove head attribute for root tokens in dependency tree and non-new sentences
		output = output.replace(' head="#u0"',"").replace(' new_sent="false"',"")

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

	if do_entities:
		output = analyze_entities(depedited, output, preloaded, sgml_mode, do_identities=do_identities, docname=docname)
		if sgml_mode == "conllu":
			return output  # All done if conllu output needed, else continue to merge rest
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
Add norm, lemma, parse, tag, entities, identities, unary tags, find multiword expressions and do language recognition:
> python coptic_nlp.py -penmultri infile.txt        

Just tokenize a file using pipes and dashes:
> python coptic_nlp.py -o pipes infile.txt       

Tokenize with pipes and mark up line breaks, conservatively detokenize bound groups, assume seg boundary at merge site:
> python coptic_nlp.py -b -d 1 --segment_merged -o pipes infile.txt

Normalize, tag, lemmatize, find multiword expressions and parse, splitting sentences by <verse> tags:
> python coptic_nlp.py -pnltm -s verse infile.txt       

Add full analyses to a whole directory of *.xml files, output to a specified directory:    
> python coptic_nlp.py -penmult --dirout /home/cop/out/ *.xml

Parse a tagged SGML file into CoNLL tabular format for treebanking, use translation tag to recognize sentences:
> python coptic_nlp.py --no_tok --parse_only --pos_spans -s translation infile.tt

Merge a parse into a tagged SGML file's <norm> tags, use translation tag to recognize sentences:
> python coptic_nlp.py --merge_parse --pos_spans -s translation infile.tt

Add entities to a tagged SGML file with translation spans but without a parse:

> python coptic_nlp.py --merge_parse -r -s translation infile.tt
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
	g1.add_argument("-r","--recognize_entities", action="store_true", help='Add entity type recognition')
	g1.add_argument("-i","--identities", action="store_true", help='Add entity linking to Wikipedia')
	g1.add_argument("-s","--sent", action="store", help='XML tag to split sentences, e.g. verse for <verse ..> (otherwise PUNCT tag is used to split sentences)')
	g1.add_argument("-o","--outmode", action="store", choices=["pipes","sgml","conllu"], default="sgml", help='Output SGML, conllu or tokenize with pipes')

	g2 = parser.add_argument_group("less common options")
	g2.add_argument("-f","--finitestate", action="store_true", help='Use old finite-state tokenizer (less accurate)')
	g2.add_argument("-d","--detokenize", action="store", type=int, choices=[0,1,2,3], default=0, help="Re-group non-standard bound groups (a.k.a. 'laytonize') - 1=conservative 2=aggressive 3=smart")
	g2.add_argument("--segment_merged", action="store_true", help="When re-grouping bound groups, assume merged groups have segmentation boundary between them")
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
	g2.add_argument("--treetagger", action="store_true", help='Tag using TreeTagger instead of flair')
	g2.add_argument("--marmot", action="store_true", help='Tag using Marmot instead of flair')
	g2.add_argument("--malt", action="store_true", help='Parse using MaltParser instead of Diaparser (requires Java)')
	g2.add_argument("--no_gold_parse", action="store_true", help='Do not use UD_Coptic cache for gold parses')
	g2.add_argument("--processing_meta", action="store_true", help='Add segmentation/tagging/parsing/entities="auto"')

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

	preloaded = {"stk":None, "tagger": None, "xrenner":None, "parser":None}
	if dotok and not old_tokenizer:
		# Pre-load stacked tokenizer for entire batch
		preloaded["stk"] = StackedTokenizer(pipes=opts.outmode == "pipes", lines=opts.breaklines, tokenized=opts.from_pipes,
							   segment_merged=opts.segment_merged, detok=opts.detokenize)
	else:
		preloaded["stk"] = None

	if opts.tag and not (opts.treetagger or opts.marmot):
		preloaded["tagger"] = FlairTagger(train=False)

	if opts.parse or opts.parse_only or opts.merge_parse:
		if preloaded["parser"] is None:
			with suppress_stdout_stderr():
				preloaded["parser"] = NeuralParser.load(neural_model)

	if opts.recognize_entities:
		from xrenner import Xrenner  # .lib
		xrenner = Xrenner(model=lib_dir + "cop.xrm")
		preloaded["xrenner"] = xrenner

	# Check if TreeTagger and Malt Parser are available
	tt_OK, malt_OK, foma_OK, marmot_OK = check_requirements()
	if (opts.tag and not marmot_OK) or ((opts.parse or opts.parse_only or opts.merge_parse) and opts.malt and not malt_OK) or \
			(opts.tag and opts.treetagger and not tt_OK) or not foma_OK:
		sys.stderr.write("! You are missing required software:\n")
		if not foma_OK and (opts.norm or not opts.no_tok):
			sys.stderr.write(" - Foma is not installed but is required for tokenization and normalization\n")
		if opts.tag and not marmot_OK and not opts.treetagger:
			sys.stderr.write(" - Tagging is specified but Marmot is not installed\n")
		if opts.tag and opts.treetagger and not tt_OK:
			sys.stderr.write(" - Tagging is specified but TreeTagger is not installed\n")
		if (opts.parse or opts.parse_only or opts.merge_parse) and opts.malt and not malt_OK:
			sys.stderr.write(" - Parsing with Malt is specified but Malt Parser 1.8 is not installed\n")
		response = inp("Attempt to download missing software? [Y/N]\n")
		if response.upper().strip() == "Y":
			download_requirements(tt_OK,malt_OK,foma_OK,marmot_OK,require_tt=opts.treetagger, require_malt=opts.malt)
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
			if infile.endswith("." + opts.extension) and opts.dirout == ".":
				outfile = base.replace("." + opts.extension,".out." + opts.extension)
			elif len(infile) > 4 and infile[-4] == ".":
				outfile = base[:-4] + "." + opts.extension
			elif len(infile) > 4 and infile[-3:] == ".tt":
				outfile = base[:-3] + "." + opts.extension
			else:
				outfile = base + "." + opts.extension
		elif opts.outmode == "conllu":
			opts.extension = "conllu"
		else:
			outfile = base + ".out.txt"

		if not opts.quiet:
			sys.stderr.write("Processing " + base + "\n")

		if opts.identities and not (opts.recognize_entities):
			sys.stderr.write("o --identities was selected, which requires entities; turning on --recognize_entities")
			opts.recognize_entities = True

		if opts.recognize_entities and not (opts.parse or opts.parse_only or opts.merge_parse):
			sys.stderr.write("o --recognize_entities was selected, which requires parsing; turning on --parse option")
			opts.parse = True

		if opts.identities:
			from lib.identify import Identifier
			identifier = Identifier()

		input_text = io.open(infile,encoding="utf8").read()
		if opts.space:
			input_text = space_punct(input_text)

		if opts.para:
			input_text = ekthetic_to_para(input_text)

		if opts.merge_parse and not opts.pos_spans:
			sys.stderr.write("o --merge_parse was selected; turning on --pos_spans option")
			opts.pos_spans = True

		if not opts.no_gold_parse and (opts.parse or opts.parse_only or opts.merge_parse or opts.recognize_entities):
			get_gold_trees()

		if opts.treetagger:
			tagger_type = "treetagger"
		elif opts.marmot:
			tagger_type = "marmot"
		else:
			tagger_type = "flair"

		if opts.malt:
			parser_type = "malt"
		else:
			parser_type = "diaparser"

		processed = nlp_coptic(input_text, lb=opts.breaklines, parse_only=opts.parse_only, do_tok=dotok,
							   do_norm=opts.norm, do_mwe=opts.multiword, do_tag=opts.tag, do_lemma=opts.lemma,
							   do_lang=opts.etym, do_milestone=opts.unary, do_parse=opts.parse, sgml_mode=opts.outmode,
							   tok_mode="auto", old_tokenizer=old_tokenizer, sent_tag=opts.sent, preloaded=preloaded,
							   pos_spans=opts.pos_spans, merge_parse=opts.merge_parse, detokenize=opts.detokenize,
							   segment_merged=opts.segment_merged, tagger=tagger_type, parser=parser_type,
							   do_entities=opts.recognize_entities, no_gold_parse=opts.no_gold_parse,
							   do_identities=opts.identities, docname=base)

		if opts.outmode == "sgml":
			if opts.processing_meta:  # NLP reliability metadata
				seg = 'segmentation="automatic"' if not opts.from_pipes else 'segmentation="checked"'
				proc_meta = [seg]
				if opts.merge_parse:
					tagging = 'tagging="checked'
					parsing = 'parsing="checked"'
					proc_meta += [tagging, parsing]
				else:
					if opts.tag:
						tagging = 'tagging="automatic"' if not opts.pos_spans else 'tagging="checked"'
						proc_meta.append(tagging)
					if opts.parse:
						parsing = 'parsing="automatic"'
						proc_meta.append(parsing)
				if opts.recognize_entities:
					proc_meta.append('entities="automatic"')
				if opts.identities:
					proc_meta.append('identities="automatic"')
				if "<meta " in processed:
					processed = processed.replace("<meta ","<meta " + " ".join(proc_meta) + " ")
				else:
					processed = "<meta " + " ".join(proc_meta) + ">\n" + processed
				if "</meta>" not in processed:
					processed = processed.strip() + "\n</meta>\n"

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
