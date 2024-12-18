"""
flair_pos_tagger.py
"""

from argparse import ArgumentParser
import flair
from flair.data import Corpus, Sentence
from flair.datasets import ColumnCorpus
from flair.embeddings import OneHotEmbeddings, TransformerWordEmbeddings, StackedEmbeddings, WordEmbeddings
from flair.models import SequenceTagger
import os, io, re
from collections import defaultdict
from glob import glob
from depedit import DepEdit
from random import seed, shuffle
seed(42)

flair_version = int(flair.__version__.split(".")[1])

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
model_dir = script_dir + ".." + os.sep + "lib" + os.sep
GIT_ROOT = "C:\\Uni\\Coptic\\git\\"  # Path to parent of clones of CopticScriptorium/Corpora and UniversalDependencies/UD_Coptic-Scriptorium (and/or Bohairic)
CONLLU_ROOT = GIT_ROOT + "UD_Coptic" + os.sep  # Path to conllu
PUB_CORPORA = GIT_ROOT + "corpora" + os.sep + "pub_corpora" + os.sep  # Path to CopticScriptorium/Corpora
TARGET_FEATS = {"Gender","Number","Tense","VerbForm","Voice"}


class FlairTagger:

    def __init__(self, train=False, morph=False, seg=False, lang="cop"):
        global model_dir
        lang = "boh" if lang.lower().startswith("boh") else "cop"
        self.dialect = lang
        if seg:
            model_dir = "models" + os.sep
            self.model = SequenceTagger.load(model_dir + lang + ".seg")
        elif not train:
            if morph:
                self.model = SequenceTagger.load(model_dir + lang + ".morph")
            else:
                self.model = SequenceTagger.load(model_dir + lang + ".flair")

    def make_seg_data(self):
        # TODO: adapt to Coptic
        global CONLLU_ROOT
        global GIT_ROOT

        prefixes = {"ב","כ","מ","ל","ה",}
        suffixes = {"ו","ה","י","ך","ם","ן","הם","הן","כם","כן","יו"}
        def segs2tag(segs):
            tag = "X"
            if len(segs) == 2:
                if segs[0] == "ו":
                    tag = "W"
                elif segs[0] in ["ש","כש"]:
                    tag = "S"
                elif segs[0] in prefixes:
                    tag = "B"
                if segs[1] in suffixes:
                    tag += "Y"
            elif len(segs) == 3:
                if segs[0] == "ו":
                    tag = "W"
                elif segs[0] in ["ש","כש"]:
                    tag = "S"
                elif segs[0] in prefixes:
                    tag = "B"
                if segs[1] in ["ש","כש"]:
                    tag += "S"
                elif segs[1] in prefixes:
                    tag += "B"
                if segs[2] in suffixes:
                    tag += "Y"
            elif len(segs) > 3:
                if segs[0] == "ו":
                    tag = "W"
                elif segs[0] in ["ש","כש"]:
                    tag = "S"
                if segs[1] in ["ש","כש"]:
                    tag += "S"
                elif segs[1] in prefixes:
                    tag += "B"
                if segs[2] in prefixes:
                    tag += "B"
                if segs[-1] in suffixes:
                    tag += "Y"
            if tag == "BS":
                tag = "BB"  # מ+ש, כ+ש
            elif tag == "WSY":  # ושעיקרה
                tag = "WBY"
            elif "XS" in tag:
                tag = "X"
            return tag

        def conllu2segs(conllu, target="affixes"):
            super_length = 0
            limit = 4  # Maximum bound group length in units, discard sentences with longer groups
            sents = []
            words = []
            labels = []
            word = []
            max_len = 0
            lines = conllu.split("\n")
            for line in lines:
                if "\t" in line:
                    fields = line.split("\t")
                    if "-" in fields[0]:
                        start, end = fields[0].split("-")
                        super_length = int(end) - int(start) + 1
                    else:
                        if super_length > 0:
                            word.append(fields[1])
                            super_length -= 1
                            if super_length == 0:
                                words.append("".join(word))
                                if target=="count":
                                    labels.append(str(len(word)))
                                else:
                                    labels.append(segs2tag(word))
                                if len(word) > max_len:
                                    max_len = len(word)
                                word = []
                        else:
                            words.append(fields[1])
                            labels.append("O")
                elif len(line) == 0 and len(words) > 0:
                    if max_len > limit or " " in "".join(words):  # Reject sentence
                        max_len = 0
                    else:
                        sents.append("\n".join([w + "\t" + l for w, l, in zip(words,labels)]))
                    words = []
                    labels = []
            return "\n\n".join(sents)

        if self.dialect == "boh":
            CONLLU_ROOT = GIT_ROOT + "UD_Bohairic" + os.sep
        files = glob(CONLLU_ROOT + "seg" + os.sep + "*.conllu")
        data = ""
        for file_ in files:
            data += conllu2segs(io.open(file_,encoding="utf8").read()) + "\n\n"
        sents = data.strip().split("\n\n")
        sents = list(set(sents))
        shuffle(sents)
        with io.open("tagger" + os.sep + "heb_train_seg.txt", 'w', encoding="utf8",newline="\n") as f:
            f.write("\n\n".join(sents[:int(-len(sents)/10)]))
        with io.open("tagger" + os.sep + "heb_dev_seg.txt", 'w', encoding="utf8",newline="\n") as f:
            f.write("\n\n".join(sents[int(-len(sents)/10):]))
        with io.open("tagger" + os.sep + "heb_test_seg.txt", 'w', encoding="utf8",newline="\n") as f:
            f.write("\n\n".join(sents[int(-len(sents)/10):]))

    @staticmethod
    def sgml2conll(sgml, doc, corpus):
        def make_upos(cs_tag, func):
            out_tag = ""
            if cs_tag == "AAOR":
                out_tag = "AUX"
            if cs_tag == "ACAUS":
                out_tag = "VERB"
            if cs_tag == "ACOND":
                out_tag = "SCONJ"
            if cs_tag == "ACONJ":
                out_tag = "AUX"
            if cs_tag == "ADV":
                out_tag = "ADV"
            if cs_tag == "AFUTCONJ":
                out_tag = "AUX"
            if cs_tag == "AJUS":
                out_tag = "AUX"
            if cs_tag == "ALIM":
                out_tag = "SCONJ"
            if cs_tag == "ANEGAOR":
                out_tag = "AUX"
            if cs_tag == "ANEGJUS":
                out_tag = "AUX"
            if cs_tag == "ANEGOPT":
                out_tag = "AUX"
            if cs_tag == "ANEGPST":
                out_tag = "AUX"
            if cs_tag == "ANY":
                out_tag = "AUX"
            if cs_tag == "AOPT":
                out_tag = "AUX"
            if cs_tag == "APREC":
                out_tag = "SCONJ"
            if cs_tag == "APST":
                out_tag = "AUX"
            if cs_tag == "ART":
                out_tag = "DET"
            if cs_tag == "CCIRC":
                out_tag = "SCONJ"
            if cs_tag == "CFOC":
                out_tag = "PART"
            if cs_tag == "CONJ":
                if func == "mark":
                    out_tag = "SCONJ"
                else:
                    out_tag = "CCONJ"
            if cs_tag == "COP":
                out_tag = "PRON"
            if cs_tag == "CPRET":
                out_tag = "AUX"
            if cs_tag == "CREL":
                out_tag = "SCONJ"
            if cs_tag == "EXIST":
                out_tag = "VERB"
            if cs_tag == "FM":
                out_tag = "X"
            if cs_tag == "FUT":
                out_tag = "AUX"
            if cs_tag == "IMOD":
                out_tag = "ADV"
            if cs_tag == "N":
                if func == "amod":
                    out_tag = "ADJ"
                else:
                    out_tag = "NOUN"
            if cs_tag == "NEG":
                out_tag = "ADV"
            if cs_tag == "NPROP":
                out_tag = "PROPN"
            if cs_tag == "NUM":
                out_tag = "NUM"
            if cs_tag == "PDEM":
                out_tag = "DET"
            if cs_tag == "PINT":
                out_tag = "PRON"
            if cs_tag == "PPERI":
                out_tag = "PRON"
            if cs_tag == "PPERO":
                out_tag = "PRON"
            if cs_tag == "PPERS":
                out_tag = "PRON"
            if cs_tag == "PPOS":
                out_tag = "DET"
            if cs_tag == "PREP":
                if func == "mark":
                    out_tag = "PART"
                else:
                    out_tag = "ADP"
            if cs_tag == "PTC":
                out_tag = "PART"
            if cs_tag == "PUNCT":
                out_tag = "PUNCT"
            if cs_tag == "UNKNOWN":
                out_tag = "X"
            if cs_tag == "FW":
                out_tag = "X"
            if cs_tag == "V":
                out_tag = "VERB"
            if cs_tag == "VBD":
                out_tag = "VERB"
            if cs_tag == "VIMP":
                out_tag = "VERB"
            if cs_tag == "VSTAT":
                out_tag = "VERB"
            if cs_tag.endswith("_PPERS"):
                out_tag = "PRON"
            if cs_tag.endswith("_PPERO"):
                out_tag = "PRON"
            if cs_tag == "_":  # supertoken
                out_tag = "_"
            if func == "aux":
                out_tag = "AUX"
            if cs_tag == "PINT" and func == "advmod":
                out_tag = "ADV"

            return out_tag

        def make_sid(sent_num):
            sid = str(sent_num)
            if len(sid) == 1:
                sid = "s000" + sid
            elif len(sid) == 2:
                sid = "s00" + sid
            elif len(sid) == 3:
                sid = "s0" + sid
            else:
                sid = "s" + sid
            return sid

        def lang2iso(lang):
            if lang == "Hebrew":
                return "he"
            elif lang == "Greek":
                return "grc"
            elif lang == "Latin":
                return "la"
            elif lang == "Egyptian":
                return "egy"
            elif lang == "Akkadian":
                return "akk"
            elif lang == "Aramaic":
                return "arc"
            elif lang == "Arabic":
                return "ara"
            elif lang == "Persian":
                return "peo"
            else:
                raise IOError("Uknnown language code: " + lang + "\n")

        def get(attr, line):
            return re.search(" " + attr + '="([^"]*)"', line).group(1)

        def make_sent(sent, sent_num, text, trans):
            sid = "# sent_id = " + corpus + "-" + doc + "_" + make_sid(sent_num)
            sid = sid.replace(".", "_")
            s_text = "# text = " + " ".join(text)
            trans = trans.replace("&apos;", "'")
            sent = [sid, s_text, "# text_en = " + trans] + sent + [""]
            return sent

        """Take a TT SGML file including parses and create Scriptorium-style CoNLLU"""
        # See if we have sentence spans in treebank
        norms = sgml.count("</norm>")
        trans = sgml.count("</translation>")
        do_trans = False
        break_indices = set([])

        groups = {}
        entity_starts = defaultdict(list)
        entity_ends = defaultdict(list)
        entity_single = {}
        entity_stack = []
        norms = []
        langs = []
        lang = ""
        counter = 0
        start = 1
        ent_start = 1
        lines = sgml.split("\n")
        # First pass - get bound groups and entities
        for l, line in enumerate(lines):
            if "ϩⲁⲣⲙⲁ" in line:
                a = 3
            if " norm_group=" in line:
                start = counter + 1
            if "</norm_group>" in line:
                end = counter
                groups[start] = (end, "".join(norms))
                norms = []
            if ' entity="' in line:
                ent_type = get("entity", line)
                ident = ""
                if " identity=" in line:
                    ident = get("identity", line).replace(" ", "_").replace("(", "%28").replace(")", "%29")
                entity_starts[counter + 1].append((ent_type, ident))
                entity_stack.append((ent_type, counter + 1, ident))
            if " lang=" in line:
                lang = get("lang", line)
            if "</norm>" in line:
                langs.append(lang)
                lang = ""
            if "</entity>" in line:
                ent_type, ent_start, ident = entity_stack.pop()
                if ent_start < counter:
                    entity_ends[counter].append((ent_type, ident))
                else:
                    entity_single[counter] = (ent_type, ident)
                    # Now remove a single occurrence of this entity type from entity_starts
                    prev_len = len(entity_starts[counter])
                    entity_starts[counter].remove((ent_type, ident))
                    assert len(entity_starts[counter]) == prev_len - 1
            if " norm=" in line:
                norm = get("norm", line)
                norms.append(norm)
                counter += 1

        # output = ["# newdoc id = " + corpus + ":" + conllize_name(doc)]
        output = ["# newdoc id = " + corpus + ":" + doc]
        sent_tag = "translation" if "</translation>" in sgml else "verse_n"
        tok = xml_id = head = sent_num = 1
        offset = 0
        trans = ""
        orig = word = pos = lemma = func = ""
        sent = []
        morphs = []
        text = []
        for line in lines:
            if ' norm="' in line:
                word = get("norm", line)
            if ' orig="' in line:
                orig = get("orig", line)
            if ' pos="' in line:
                pos = get("pos", line)
            if " lemma=" in line:
                lemma = get("lemma", line)
            if " morph=" in line:
                morphs.append(get("morph", line))
            if " func=" in line:
                func = get("func", line)
                if func == "root":
                    head = 0
            if " head=" in line:
                head = int(get("head", line).replace("#", "").replace("u", "")) - offset
            elif " func=" in line:  # item has function but not head -> is a root
                head = 0
            if " xml:id=" in line and ' norm=' in line:  # Avoid other xml:id, e.g. on <pb> element
                xml_id = int(get("xml:id", line).replace("u", ""))
            if "</norm>" in line:
                misc = []
                if len(morphs) > 0:
                    misc.append("Morphs=" + "-".join(morphs))
                if orig != word:
                    misc.append("Orig=" + orig)
                ent_list = []
                if xml_id in entity_single:
                    ent_type, ident = entity_single[xml_id]
                    ent_string = ent_type if len(ident) == 0 else "-".join([ent_type, ident])
                    ent_list.append("(" + ent_string + ")")
                if xml_id in entity_ends:
                    for (ent_type, ident) in entity_ends[xml_id]:
                        ent_string = ent_type if len(ident) == 0 else "-".join([ent_type, ident])
                        ent_list.append(ent_string + ")")
                if xml_id in entity_starts:
                    for (ent_type, ident) in entity_starts[xml_id]:
                        ent_string = ent_type if len(ident) == 0 else "-".join([ent_type, ident])
                        ent_list.append("(" + ent_string)
                if len(ent_list) > 0:
                    misc.append("Entity=" + "".join(ent_list))
                if langs[tok - 1] != "":
                    misc.append("OrigLang=" + lang2iso(langs[tok - 1]))

                misc = "|".join(sorted(misc))
                if misc == "":
                    misc = "_"
                if xml_id in groups:
                    end, supertok = groups[xml_id]
                    if end > xml_id:
                        sent.append("\t".join([str(xml_id - offset) + "-" + str(end - offset), supertok] + ["_"] * 8))
                    text.append(supertok)
                upos = make_upos(pos, func)
                cols = [str(tok - offset), word, lemma, upos, pos, "_", str(head), func, "_", misc]
                sent.append("\t".join(cols))
                tok += 1
                morphs = []
            if "<" + sent_tag in line:
                if " translation=" in line:
                    trans = get("translation", line)
                else:
                    trans = "..."
            if len(break_indices) > 0:
                if tok in break_indices:  # New sentence
                    if trans == "" or not do_trans:
                        trans = "..."
                    if len(sent) > 0:
                        sent = make_sent(sent, sent_num, text, trans)
                        output += sent
                        offset = xml_id
                        sent = []
                        text = []
                        sent_num += 1
                        if len(break_indices) > 1:
                            break_indices.remove(tok)
            elif "</" + sent_tag in line:  # No treebank sentence spans, use translation spans
                sent = make_sent(sent, sent_num, text, trans)
                output += sent
                offset = xml_id
                sent = []
                text = []
                sent_num += 1
        conll = "\n".join(output) + "\n\n"
        d = DepEdit(io.open("C:\\Uni\\Coptic\\git\\corpora\\treebank-dev\\merge_scripts\\add_ud_morph.ini", encoding="utf8").read().split("\n"))
        conllu = d.run_depedit(conll.split("\n"))
        return conllu.strip() + "\n\n"

    def make_all_checked(self, bohairic=False):
        files = glob(PUB_CORPORA + "**" + os.sep + "*.tt",recursive=True)
        all_conllu = []
        for file_ in files:
            sgml = open(file_).read()
            # TODO: fix Mark metadata and update file list for train set
            if 'parsing="gold' in sgml or 'tagging="auto' in sgml or "</translation>" not in sgml \
                    or "coptic-treebank" in file_:
                continue
            if ('Bohairic' in sgml or 'bohairic' in file_):
                if not bohairic:
                    continue
            else:
                if bohairic:
                    continue

            conllu = self.sgml2conll(sgml,os.path.basename(file_),file_.split(os.sep)[-2])
            all_conllu.append(conllu.strip())
        with open(script_dir + self.dialect + "_non_tb_checked_pos.conllu",'w',encoding="utf8",newline="\n") as f:
            f.write("\n\n".join(all_conllu) + "\n\n")

    def make_pos_data(self, all_checked=True, tags=False):
        global CONLLU_ROOT
        global GIT_ROOT

        def filter_morph(feats):
            if feats == "_":
                return "O"
            else:
                annos = []
                for f in feats.split("|"):
                    k, v = f.split("=")
                    if k in TARGET_FEATS:
                        annos.append(k+"="+v)
                if len(annos) > 0:
                    return "|".join(annos)
                else:
                    return "O"

        if self.dialect == "boh":
            CONLLU_ROOT = GIT_ROOT + "UD_Bohairic" + os.sep

        files = glob(CONLLU_ROOT + "*.conllu")
        train = test = dev = ""
        super_tok_len = 0
        super_tok_start = False
        suff = "_morph" if tags else ""
        if all_checked:
            self.make_all_checked(bohairic=self.dialect=="boh")
            files.append(script_dir + self.dialect + "_non_tb_checked_pos.conllu")
        for file_ in files:
            output = []
            lines = io.open(file_,encoding="utf8").readlines()
            for line in lines:
                if "\t" in line:
                    fields = line.split("\t")
                    if "." in fields[0]:
                        continue
                    if "-" in fields[0]:
                        super_tok_start = True
                        start,end = fields[0].split("-")
                        super_tok_len = int(end)-int(start) + 1
                        continue
                    if super_tok_start:
                        super_tok_position = "B"
                        super_tok_start = False
                        super_tok_len -= 1
                    elif super_tok_len > 0:
                        super_tok_position = "I"
                        super_tok_len -= 1
                        if super_tok_len == 0:
                            super_tok_position = "E"
                    else:
                        super_tok_position = "O"
                    if tags:
                        morph = filter_morph(fields[5])
                        output.append(fields[1] + "\t" + super_tok_position + "\t" + fields[4] + "\t" + morph)
                    else:
                        output.append(fields[1] + "\t" + super_tok_position + "\t" + fields[4])
                elif len(line.strip()) == 0:
                    if output[-1] != "":
                        output.append("")
            if "dev" in file_:
                dev += "\n".join(output)
            elif "test" in file_:
                test += "\n".join(output)
            else:
                train += "\n".join(output)
        with io.open("tagger" + os.sep + self.dialect + "_train"+suff+".txt", 'w', encoding="utf8",newline="\n") as f:
            f.write(train)
        with io.open("tagger" + os.sep + self.dialect + "_dev"+suff+".txt", 'w', encoding="utf8",newline="\n") as f:
            f.write(dev)
        with io.open("tagger" + os.sep + self.dialect + "_test"+suff+".txt", 'w', encoding="utf8",newline="\n") as f:
            f.write(test)

    def train(self, cuda_safe=True, positional=True, tags=False, seg=False):
        if cuda_safe:
            # Prevent CUDA Launch Failure random error, but slower:
            import torch
            torch.backends.cudnn.enabled = False
            # Or:
            # os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

        # 1. get the corpus
        # this is the folder in which train, test and dev files reside
        data_folder = "tagger" + os.sep

        # init a corpus using column format, data folder and the names of the train, dev and test files

        # define columns
        columns = {0: "text", 1: "super", 2: "pos"}
        suff = ""
        if positional:
            columns[1] = "super"
            columns[2] = "pos"
        if tags:
            columns[3] = "morph"
            suff = "_morph"
        if seg:
            columns[1] = "seg"
            del columns[2]
            self.make_seg_data()
            suff = "_seg"
        else:
            self.make_pos_data(tags=tags)

        corpus: Corpus = ColumnCorpus(
            data_folder, columns,
            train_file=self.dialect + "_train"+suff+".txt",
            test_file=self.dialect + "_test"+suff+".txt",
            dev_file=self.dialect + "_dev"+suff+".txt",
        )

        # 2. what tag do we want to predict?
        tag_type = 'pos' if not tags else "morph"
        if seg:
            tag_type = "seg"

        # 3. make the tag dictionary from the corpus
        if flair_version > 8:
            tag_dictionary = corpus.make_label_dictionary(label_type=tag_type)
        else:
            tag_dictionary = corpus.make_tag_dictionary(tag_type=tag_type)
        print(tag_dictionary)

        # 4. initialize embeddings
        #embeddings: TransformerWordEmbeddings = TransformerWordEmbeddings(data_folder + os.sep + 'bert_2_60_5',)
        #embeddings: TransformerWordEmbeddings = TransformerWordEmbeddings('lgessler/coptic-bert-small-uncased',)

        if self.dialect == "cop":
            w2v: WordEmbeddings = WordEmbeddings(script_dir + ".." + os.sep + "data" + os.sep + "coptic_50d.vec.gensim")
            embeddings: TransformerWordEmbeddings = TransformerWordEmbeddings('lgessler/microbert-coptic-mx', )
        else:
            w2v: WordEmbeddings = WordEmbeddings(script_dir + ".." + os.sep + "data.b" + os.sep + "bohairic_50d.vec.gensim")
            #embeddings: TransformerWordEmbeddings = TransformerWordEmbeddings(script_dir + ".." + os.sep + "data.b" + os.sep + "bohmbert", )
            embeddings: TransformerWordEmbeddings = TransformerWordEmbeddings('amir-zeldes/bohmbert-m')

        if positional:
            if flair_version > 8:
                positions: OneHotEmbeddings = OneHotEmbeddings.from_corpus(corpus, field='super', embedding_length=5)
            else:
                positions: OneHotEmbeddings = OneHotEmbeddings(corpus=corpus, field="super", embedding_length=5)
            if tags:
                tag_emb: OneHotEmbeddings = OneHotEmbeddings(corpus=corpus, field="pos", embedding_length=17)
                stacked: StackedEmbeddings = StackedEmbeddings([embeddings,positions,tag_emb])
            else:
                stacked: StackedEmbeddings = StackedEmbeddings([embeddings, positions, w2v])
        elif not seg:
            if tags:
                tag_emb: OneHotEmbeddings = OneHotEmbeddings(corpus=corpus, field="pos", embedding_length=17)
                stacked: StackedEmbeddings = StackedEmbeddings([embeddings,tag_emb])
            else:
                stacked = embeddings
        else:
            stacked = embeddings # StackedEmbeddings([embeddings,w2v])

        # 5. initialize sequence tagger
        tagger: SequenceTagger = SequenceTagger(hidden_size=128,
                                                embeddings=stacked,
                                                tag_dictionary=tag_dictionary,
                                                tag_type=tag_type,
                                                use_crf=True,
                                                use_rnn=True)

        # 6. initialize trainer
        from flair.trainers import ModelTrainer

        trainer: ModelTrainer = ModelTrainer(tagger, corpus)

        # 7. start training
        trainer.train(script_dir + "pos-dependencies" + os.sep + 'flair_tagger',
                      learning_rate=0.1,
                      mini_batch_size=15,
                      max_epochs=50)

    def predict(self, in_path=None, in_format="flair", out_format="conllu", as_text=False, tags=False, seg=False,
                norm="norm", group="norm_group", sent="translation"):
        model = self.model
        tagcol = 4

        if as_text:
            data = in_path
            #data = (data + "\n").replace("<s>\n", "").replace("</s>\n", "\n").strip()
        else:
            data = io.open(in_path,encoding="utf8").read()
        sents = []
        words = []
        positions = []
        group_breaks = []
        true_tags = []
        true_pos = []
        super_tok_start = False
        super_tok_len = 0
        data = data.strip() + "\n"  # Ensure final new line for last sentence
        for line in data.split("\n"):
            if len(line.strip())==0 or \
                    (in_format=="sgml" and ("</" + sent + ">" in line or (len(group_breaks)>200 and "</" + group + ">" in line))):
                if len(words) > 0:
                    if flair_version > 8:
                        tokenizer = False
                    else:
                        tokenizer = lambda x:x.split(" ")
                    sents.append(Sentence(" ".join(words),use_tokenizer=tokenizer))
                    if in_format == "sgml":  # Compute BG positions
                        for i, p in enumerate(group_breaks):
                            next_p = 0 if i == len(group_breaks) - 1 else group_breaks[i+1]
                            if p == 1:
                                if next_p == 1:
                                    positions.append("O")
                                else:
                                    positions.append("B")
                            else:
                                if next_p == 1:
                                    positions.append("E")
                                else:
                                    positions.append("I")
                    for i, word in enumerate(sents[-1]):
                        if not seg:
                            word.add_label("super",positions[i])
                        if tags:
                            word.add_label("pos",true_pos[i])
                    words = []
                    positions = []
                    true_pos = []
                    group_breaks = []
            else:
                if in_format == "flair":
                    words.append(line.split("\t")[0])
                    if not seg:
                        positions.append(line.split("\t")[1])
                    if tags:
                        true_pos.append(line.split("\t")[2])
                        true_tags.append(line.split("\t")[3]) if "\t" in line else true_tags.append("")
                    else:
                        true_tags.append(line.split("\t")[2]) if "\t" in line else true_tags.append("")
                elif in_format == "sgml":
                    if line.startswith("<") and line.endswith(">"):
                        # SGML
                        if ' ' + group + "=" in line:
                            super_tok_len = 0
                        elif " " + norm + "=" in line:
                            token = re.search(' ' + norm+'="([^"]+)"',line).group(1)
                            if super_tok_len == 0:
                                group_breaks.append(1)
                            else:
                                group_breaks.append(0)
                            words.append(token)
                            super_tok_len +=1
                        if ' pos="' in line:
                            true_pos.append(re.search(' pos="([^"]+)"',line).group(1))
                else:
                    if "\t" in line:
                        fields = line.split("\t")
                        if "." in fields[0]:
                            continue
                        if "-" in fields[0]:
                            super_tok_start = True
                            start, end = fields[0].split("-")
                            super_tok_len = int(end) - int(start) + 1
                            continue
                        if super_tok_start:
                            super_tok_position = "B"
                            super_tok_start = False
                            super_tok_len -= 1
                        elif super_tok_len > 0:
                            super_tok_position = "I"
                            super_tok_len -= 1
                            if super_tok_len == 0:
                                super_tok_position = "E"
                        else:
                            super_tok_position = "O"
                        words.append(line.split("\t")[1])
                        positions.append(super_tok_position)
                        true_tags.append(line.split("\t")[tagcol])
                        true_pos.append(line.split("\t")[4])

        # predict tags and print
        if flair_version > 8:
            model.predict(sents, force_token_predictions=True, return_probabilities_for_all_classes=True)
        else:
            model.predict(sents)#, all_tag_prob=True)

        preds = []
        scores = []
        words = []
        for i, sent in enumerate(sents):
            for tok in sent.tokens:
                if tags:
                    if flair_version > 8:
                        pred = tok.labels[2].value if len(tok.labels)>0 else "O"
                        score = tok.labels[2].score if len(tok.labels) > 0 else "1.0"
                    else:
                        pred = tok.labels[2].value
                        score = str(tok.labels[2].score)
                else:
                    if flair_version > 8:
                        pred = tok.labels[-1].value if len(tok.labels)>0 else "O"
                        score = tok.labels[-1].score if len(tok.labels) > 0 else "1.0"
                    else:
                        pred = tok.labels[1].value
                        score = str(tok.labels[1].score)
                preds.append(pred)
                scores.append(score)
                words.append(tok.text)
                tok.clear_embeddings()  # Without this, there will be an OOM issue

        toknum = 0
        output = []
        #out_format="diff"
        for i, sent in enumerate(sents):
            tid=1
            if i>0 and out_format=="conllu":
                output.append("")
            for tok in sent.tokens:
                pred = preds[toknum]
                score = str(scores[toknum])
                if len(score)>5:
                    score = score[:5]
                if out_format == "conllu":
                    pred = pred if not pred == "O" else "_"
                    fields = [str(tid),tok.text,"_",pred,pred,"_","_","_","_","_"]
                    output.append("\t".join(fields))
                    tid+=1
                elif out_format == "xg":
                    output.append("\t".join([pred, tok.text, score]))
                elif out_format == "tt":
                    output.append("\t".join([tok.text, pred]))
                else:
                    true_tag = true_tags[toknum]
                    corr = "T" if true_tag == pred else "F"
                    output.append("\t".join([pred, true_tag, corr, score, tok.text, true_pos[toknum]]))
                toknum += 1

        if as_text:
            return "\n".join(output)
        else:
            ext = "xpos.conllu" if out_format == "conllu" else "txt"
            partition = "test" if "test" in in_path else "dev"
            with io.open(script_dir + "pos-dependencies" +os.sep + "flair-"+partition+"-pred." + ext,'w',encoding="utf8",newline="\n") as f:
                f.write("\n".join(output))


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("-m","--mode",choices=["train","predict"],default="predict")
    p.add_argument("-f","--file",default=None,help="Blank for training, blank predict for eval, or file to run predict on")
    p.add_argument("-p","--positional_embeddings",action="store_true",help="Whether to use positional embeddings within supertokens (MWTs)")
    p.add_argument("-t","--tag_embeddings",action="store_true",help="Whether to use POS tag embeddings for morphology prediction")
    p.add_argument("-s","--seg",action="store_true",help="Whether to train segmentation instead of tagging")
    p.add_argument("-i","--input_format",choices=["flair","conllu"],default="flair",help="flair two column training format or conllu")
    p.add_argument("-o","--output_format",choices=["flair","conllu","xg"],default="conllu",help="flair two column training format or conllu")
    p.add_argument("-d","--dialect",choices=["sahidic","bohairic"],default="sahidic",help="dialect (Sahidic or Bohairic)")

    opts = p.parse_args()

    if opts.mode == "train":
        tagger = FlairTagger(train=True, lang=opts.dialect)
        tagger.train(positional=opts.positional_embeddings, tags=opts.tag_embeddings, seg=opts.seg)
    else:
        tagger = FlairTagger(train=False, lang=opts.dialect)
        tagger.predict(in_format=opts.input_format, out_format=opts.output_format,
                in_path=opts.file)
