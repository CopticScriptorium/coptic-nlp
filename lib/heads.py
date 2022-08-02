import re
from collections import defaultdict

class Token:

    def __init__(self, xml_id, word, pos, func, parent):
        self.xml_id = xml_id
        self.word = word
        self.pos = pos
        self.func = func
        try:
            self.parent = int(parent.replace("u",""))
        except:
            a=4

    def __repr__(self):
        return self.word + " (" + self.pos + "/" + self.func + ") <- " + str(self.parent)


class Entity:

    def __init__(self,tokens,ent_type):
        tokens.sort(key=lambda x: int(x.xml_id.replace("u","")))
        self.tokens = tokens
        self.type = ent_type
        self.start = int(tokens[0].xml_id.replace("u",""))
        self.end = int(tokens[-1].xml_id.replace("u",""))
        self.length = self.end - self.start + 1
        self.text = " ".join([t.word for t in tokens])
        self.head_token = None

    def __repr__(self):
        return self.text + " (" + str(self.start) + "-" + str(self.end) + ")"


def get(attr, line):
    return re.search(" " + attr + '="([^"]*)"', line).group(1)


def assign_entity_heads(sgml):
    def light_head_search(ent,head_position):
        light_heads = ["ⲛⲟϭ","ϩⲁϩ"]
        if ent.tokens[head_position].word in light_heads:
            light_head = ent.tokens[head_position]
            for tok in ent.tokens:
                if tok.func=="nmod" and tok.parent == int(light_head.xml_id.replace("u","")):
                    return tok
        return ent.tokens[head_position]

    def get_entity_head(ent,minimal_covering):
        head = ent.tokens[0]  # Default response
        for tok in ent.tokens:  # First minimally covered proper noun is the head
            if tok.pos == "NPROP":
                if tok in minimal_covering:
                    if minimal_covering[tok] == ent:
                        return tok
        for i, tok in enumerate(ent.tokens):
            if tok.func=="punct":
                continue
            # Non punct root or token dominated from outside the span is the head
            elif tok.parent == 0 or (tok.parent>0 and (tok.parent < ent.start or tok.parent > ent.end)):
                return light_head_search(ent,i)  # Check for ⲛⲟϭ, ϩⲁϩ etc.
        return head

    lines = sgml.strip().split("\n")
    words = {}
    entity_stack = []
    entities = []
    covering = defaultdict(set)
    minimal_covering = {}
    lines2ents = {}
    counter = 0
    norm = pos = func = xml_id = parent = ""

    # Pass 1 - collect data
    for l, line in enumerate(lines):
        if ' norm=' in line:
            norm = get("norm",line)
        if ' pos=' in line:
            pos = get("pos",line)
        if ' func=' in line:
            func = get("func",line)
        if ' xml:id=' in line and ' norm=' in line:  # Avoid other xml:id, e.g. on <pb> element
            xml_id = get("xml:id",line)
        if ' head=' in line:
            parent = get("head",line).replace("#","")
        if "</norm>" in line:
            if func == "root" or func == "punct":
                parent = "0"
            words[xml_id] = Token(xml_id,norm,pos,func,parent)
            counter += 1
        if ' entity="' in line:
            ent_type = get("entity",line)
            #entity_starts[counter + 1].append(ent_type)
            entity_stack.append((ent_type,counter+1,l))
        if '</entity>' in line:
            ent_type, ent_start, start_line = entity_stack.pop()
            ids = ["u" + str(i) for i in list(range(ent_start,counter+1))]
            try:
                tokens = [words[i] for i in ids]
            except:
                d=4
            ent = Entity(tokens, ent_type)
            entities.append(ent)
            lines2ents[start_line] = ent
            for tok in tokens:
                covering[tok].add(ent)

    # Identify semantic heads
    for tid in words:
        tok = words[tid]
        if tok in covering:
            minimal_covering[tok] = min(covering[tok],key=lambda x: x.length)

    for ent in entities:
        ent.head_token = get_entity_head(ent,minimal_covering)

    # Pass 2: assign heads
    output = []
    for l, line in enumerate(lines):
        if l in lines2ents:
            ent = lines2ents[l]
            head = "#" + ent.head_token.xml_id
            text = ent.text
            insertion = ' head_tok="'+head+'" text="'+ text + '"'
            line = line.replace(" entity",insertion + " entity")
        output.append(line)

    return "\n".join(output).strip() + "\n"