# Module for named entity identification via linking to Wikipedia
import io, os, sys, re
from collections import defaultdict

PY3 = sys.version_info[0] == 3

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
data_dir = script_dir + os.sep + ".." + os.sep + "data" + os.sep


class Identifier:

    def __init__(self):
        self.entity_heads = {}
        self.entities = {}
        self.untyped_heads = {}
        self.untyped_entities = {}
        self.link2types = defaultdict(lambda: defaultdict(int))
        self.words = {}  # Maps token ID to word for current document
        self.read_lex()
        self.links = defaultdict(set)

    def read_lex(self):
        untyped_heads = defaultdict(lambda: defaultdict(int))
        untyped_entities = defaultdict(lambda: defaultdict(int))
        lines = io.open(data_dir + "identities.tab",encoding="utf8").read().strip().split("\n")
        for line in lines:
            if "\t" in line and not line.startswith("#"):
                fields = line.split("\t")
                text, head, etype, link, freq = fields
                freq = int(freq)
                if (text, etype) not in self.entities:
                    self.entities[(text, etype)] = (link, freq)
                elif self.entities[(text, etype)][1] < freq:
                    self.entities[(text, etype)] = (link, freq)
                if (head, etype) not in self.entity_heads:
                    self.entity_heads[(head, etype)] = (link, freq)
                elif self.entity_heads[(head, etype)][1] < freq:
                    self.entity_heads[(head, etype)] = (link, freq)
                untyped_entities[text][link] += freq
                untyped_heads[head][link] += freq
                self.link2types[link][etype] += freq
        for text in untyped_entities:
            link = max(untyped_entities[text], key=lambda x:untyped_entities[text][x])
            self.untyped_entities[text] = link
        for head in untyped_heads:
            link = max(untyped_heads[head], key=lambda x:untyped_heads[head][x])
            self.untyped_heads[head] = link

    def predict(self, text, head, etype, docname=None):
        if (text, etype) in self.entities:
            return self.entities[(text,etype)][0], etype
        elif text in self.untyped_entities:
            link = self.untyped_entities[text]
            if etype in self.link2types[link]:
                return link, etype
            else:
                return link, max(self.link2types[link], key=lambda x: self.link2types[link][x])
        elif (head, etype) in self.entity_heads:
            return self.entity_heads[(head,etype)][0], etype
        elif head in self.untyped_heads:
            link = self.untyped_heads[head]
            if etype in self.link2types[link]:
                return link, etype
            else:
                return link, max(self.link2types[link], key=lambda x: self.link2types[link][x])
        else:
            return "", etype

    @staticmethod
    def get(line, attr):
        return re.search(' ' + attr + '="([^"]+)"', line).group(1)

    def predict_single_tag(self, entity_tag):
        text = self.get(entity_tag, "text")
        etype = self.get(entity_tag, "entity")
        head = self.get(entity_tag, "head_tok")
        head_word, head_pos = self.words[head.replace("#","")]
        if head_pos == "NPROP":
            link, pred_etype = self.predict(text, head_word, etype)
            if link == "":
                return entity_tag
            else:
                if pred_etype != etype:
                    entity_tag = re.sub(r'entity="[^"]+"','entity="'+pred_etype+'"',entity_tag)
                entity_tag = entity_tag.replace(" entity=",' identity="'+link+'"'+" entity=")
                self.links[etype].add(link)
                return entity_tag
        else:
            return entity_tag

    def predict_sgml(self, sgml):
        self.links = defaultdict(set)
        output = []
        for line in sgml.split("\n"):
            if ' entity=' in line:
                line = self.predict_single_tag(line)
            output.append(line)
        if '<meta ' in sgml:
            meta_index = [i for i, l in enumerate(output) if l.startswith("<meta ")][0]
            places = "; ".join(sorted(list(self.links["place"])))
            people = "; ".join(sorted(list(self.links["person"])))
            ident_meta = ""
            if people != "":
                ident_meta += ' people="' + people + '"'
            if places != "":
                ident_meta += ' places="' + places + '"'
            output[meta_index] = output[meta_index].replace("<meta","<meta" + ident_meta)
        return "\n".join(output)

    def read_words(self, sgml):
        words = {}
        lines = sgml.strip().split("\n")
        for line in lines:
            if ' norm=' in line and ' xml:id' in line:
                tid = self.get(line, "xml:id")
                word = self.get(line, "norm")
                pos = self.get(line, "pos")
                words[tid] = (word, pos)
        self.words = words
