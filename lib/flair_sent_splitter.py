from flair.data import Corpus, Sentence, Dictionary
from flair.datasets import ColumnCorpus
from flair.embeddings import WordEmbeddings, StackedEmbeddings, TransformerWordEmbeddings, OneHotEmbeddings, CharacterEmbeddings
from flair.models import SequenceTagger
import flair
from glob import glob
import os, re, io
from collections import defaultdict

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
flair_splitter_dep_dir = script_dir + "sent-dependencies" + os.sep
flair_data_dir = flair_splitter_dep_dir + "data" + os.sep
flair_version = int(flair.__version__.split(".")[1])


class FlairSentSplitter:

    def __init__(self, train=False, span_size=20, stride_size=10):

        self.span_size = span_size  # Each shingle is 20 tokens by default
        self.stride_size = stride_size  # Tag a shingle every stride_size tokens
        if not train:
            self.load_model()

    def make_train(self, use_supplement=True):
        files = glob(flair_splitter_dep_dir + "*_resent.conllu")
        from random import shuffle, seed
        data = {"train": "", "dev": "", "test": ""}
        for i, f in enumerate(files):
            partition = "train"
            if 'test' in f:
                partition = "test"
            elif 'dev' in f:
                partition = "dev"
            conllu = open(f).read()
            table, pos_tags = self.conllu2tab(conllu, span_size=self.span_size)
            data[partition] = table

        for partition in data:
            if use_supplement and partition == "train":
                supplement = open(flair_splitter_dep_dir + "supplemental_sents.tab", 'r', encoding="utf8").read()
                data[partition] = data[partition].strip() + "\n\n" + supplement
            with open(flair_data_dir + "sent_" + partition + ".txt", 'w', encoding="utf8", newline="\n") as f:
                f.write(data[partition])

    @staticmethod
    def conllu2tab(conllu, span_size=20, space_spans=True):
        counter = 0
        bg_len = -1
        bg_label = "S"
        output = []
        pos_tags = []
        for line in conllu.split("\n"):
            if "\t" in line:
                fields = line.split("\t")
                if "." in fields[0]:
                    continue
                elif "-" in fields[0]:
                    start, end = fields[0].split("-")
                    bg_len = int(end) - int(start) + 1
                    bg_label = "B"
                else:
                    label = "O"
                    pos_tags.append(fields[4])
                    if 'NewSent=Yes' in fields[-1]:
                        label = "SENT"
                    if counter == span_size + 1:
                        if space_spans:
                            output.append("")
                        counter = 0
                    output.append(fields[1] + "\t" + bg_label + "\t" + label)
                    if label == "SENT" and bg_label in ["E","I"]:
                        raise ValueError("Sentences should not start inside a bound group!")
                    if bg_label != "S":
                        if bg_len > 2:
                            bg_label = "I"
                        else:
                            bg_label = "E"
                    if bg_len > 1:
                        bg_len -= 1
                    else:
                        bg_label = "S"
                        bg_len = -1
                    counter += 1
        return "\n".join(output), pos_tags

    @staticmethod
    def tt2tab(tt, span_size=20, space_spans=True):
        output = []
        buffer = []
        groups = []
        pos_tags = []
        lines = tt.strip().split("\n")
        counter = 0
        for l, line in enumerate(lines[::-1]):
            if ' norm="' in line:
                norm = re.search(r' norm="([^"]+)"', line).group(1)
                buffer.append(norm)
            elif ' norm_group="' in line:
                groups.append(buffer)
                buffer = []
            if ' pos=' in line:
                pos = re.search(r' pos="([^"]+)"', line).group(1)
                pos_tags.append(pos)
            if '<translation translation=' in line or (not space_spans and ('</norm_group>' in line or l == len(lines)-1) and len(groups) > 0):
                groups.reverse()
                for g, group in enumerate(groups):
                    label = "O" if g > 0 else "SENT"
                    if not space_spans:
                        label = "O"
                    for i in range(len(group)):
                        if len(group) == 1:
                            bg_label = "S"
                        elif i == 0:
                            bg_label = "E"
                        elif i == len(group) - 1:
                            bg_label = "B"
                        else:
                            bg_label = "I"
                        output.append(group[i] + "\t" + bg_label + "\t" + label)
                        if label == "SENT" and bg_label in ["E", "I"]:
                            raise ValueError("Sentences should not start inside a bound group!")
                        counter += 1
                        if counter == span_size:
                            if space_spans:
                                output.append("")
                                counter = 0
                groups = []
        output.reverse()
        pos_tags.reverse()
        return "\n".join(output), pos_tags

    def load_model(self):
        model = script_dir + "cop.sent"
        self.model = SequenceTagger.load(model)

    def train(self, training_dir=None):
        from flair.trainers import ModelTrainer

        if training_dir is None:
            training_dir = flair_splitter_dep_dir

        # define columns
        columns = {0: "text", 1: "position", 2: "ner"}

        # this is the folder in which train, test and dev files reside
        data_folder = flair_splitter_dep_dir + "data"
        self.make_train()

        # init a corpus using column format, data folder and the names of the train, dev and test files
        corpus: Corpus = ColumnCorpus(
            data_folder,
            columns,
            train_file="sent_train.txt",
            test_file="sent_test.txt",
            dev_file="sent_dev.txt",
        )

        print(corpus)

        tag_type = "ner"
        if flair_version > 8:
            tag_dictionary = corpus.make_label_dictionary(label_type=tag_type)
        else:
            tag_dictionary = corpus.make_tag_dictionary(tag_type=tag_type)
        print(tag_dictionary)

        # initialize embeddings
        #char_dict = Dictionary.load(flair_splitter_dep_dir + "common_characters_large")
        #chars: CharacterEmbeddings = CharacterEmbeddings(char_dict)
        fixed: WordEmbeddings = WordEmbeddings(flair_splitter_dep_dir + "coptic_50d_bgs.vec.gensim")
        embeddings: TransformerWordEmbeddings = TransformerWordEmbeddings('lgessler/microbert-coptic-mx')
        #embeddings: TransformerWordEmbeddings = TransformerWordEmbeddings('lgessler/microelectra-coptic')
        positions: OneHotEmbeddings = OneHotEmbeddings.from_corpus(corpus, field='position', embedding_length=4)
        embeddings: StackedEmbeddings = StackedEmbeddings(embeddings=[embeddings, positions, fixed])

        tagger: SequenceTagger = SequenceTagger(
            hidden_size=128, embeddings=embeddings, tag_dictionary=tag_dictionary, tag_type=tag_type, use_crf=False,
            use_rnn=False
        )

        trainer: ModelTrainer = ModelTrainer(tagger, corpus)

        trainer.train(training_dir,
                      mini_batch_size=8,
                      max_epochs=80)
        self.model = tagger

    def predict(self, tt_sgml, in_format="tt", outmode="binary", as_text=True, as_bound_groups=True):
        if self.model is None:
            self.load_model()

        final_mapping = {}  # Map each contextualized token to its (sequence_number, position)
        spans = []  # Holds flair Sentence objects for labeling

        toks = []
        bg_labels = []

        if not as_text:
            tt_sgml = open(tt_sgml).read()

        if in_format == "tt":
            data, pos_tags = self.tt2tab(tt_sgml, space_spans=False)
        else:
            data, pos_tags = self.conllu2tab(tt_sgml, space_spans=False)

        for line in data.strip().split("\n"):
            fields = line.split("\t")
            toks.append(fields[0])
            bg_labels.append(fields[1])

        # Hack tokens up into overlapping shingles
        wraparound = toks[-self.stride_size :] + toks + toks[: self.span_size]
        wrap_bg_labels = bg_labels[-self.stride_size :] + bg_labels + bg_labels[: self.span_size]
        idx = 0
        mapping = defaultdict(set)
        snum = 0
        while idx < len(toks):
            if idx + self.span_size < len(wraparound):
                span = wraparound[idx : idx + self.span_size]
                bgs = wrap_bg_labels[idx : idx + self.span_size]
            else:
                span = wraparound[idx:]
                bgs = wrap_bg_labels[idx:]
            if flair_version > 8:
                tokenizer = False
            else:
                tokenizer = lambda x: x.split(" ")
            sent = Sentence(" ".join(span), use_tokenizer=tokenizer)
            for i, bg in enumerate(bgs):
                if flair_version < 8:
                    sent[i].add_tag("position", bg)
                else:
                    sent[i].add_label("position", bg)
            spans.append(sent)

            for i in range(idx - self.stride_size, idx + self.span_size - self.stride_size):
                # start, end, snum
                if i >= 0 and i < len(toks):
                    mapping[i].add((idx - self.stride_size, idx + self.span_size - self.stride_size, snum))
            idx += self.stride_size
            snum += 1

        for idx in mapping:
            best = self.span_size
            for m in mapping[idx]:
                start, end, snum = m
                dist_to_end = end - idx
                dist_to_start = idx - start
                delta = abs(dist_to_end - dist_to_start)
                if delta < best:
                    best = delta
                    final_mapping[idx] = (snum, idx - start)  # Get sentence number and position in sentence

        # Predict
        if flair_version > 8:
            self.model.predict(spans, force_token_predictions=True, return_probabilities_for_all_classes=True)
            preds = spans
        else:
            preds = self.model.predict(spans)#, all_tag_prob=True)

        labels = []
        last_bg_start = 0
        for idx in final_mapping:
            snum, position = final_mapping[idx]
            if flair_version < 8:
                label = 0 if preds[snum].tokens[position].tags["ner"].value == "O" else 1
            else:
                if len(preds[snum].tokens[position].labels) == 1:  # O class, no label predicted for sent position
                    label = 0
                else:
                    label = 0 if preds[snum].tokens[position].labels[1].value == "O" else 1
            bg_pos = bg_labels[idx]
            if bg_pos in ["B","S"]:
                last_bg_start = idx
            elif label == 1:  # Predicted sentence start mid bound group
                if last_bg_start != idx:
                    labels[last_bg_start] = 1
                    label = 0

            labels.append(label)

        # Filter out implausible predictions
        break_next = False
        prev_break = 0
        bad_starts = ["ACONJ", "CREL", "CCIRC", "ACONJ_PPERS", "ALIM"]
        labels[0] = 1  # First token must be a new sentence
        for i in range(len(labels)):
            pred = labels[i]
            pos = pos_tags[i]
            if break_next and pos != "PUNCT":
                labels[i] = 1
                break_next = False
            if pos == "PUNCT" and pred == 1 and i > 0:
                labels[i] = 0
                break_next = True
            if pos in bad_starts and pred == 1:
                next_breaks = [j for j in range(i + 1, len(labels)) if labels[j] == 1]
                if len(next_breaks) > 0:
                    next_break = min(next_breaks)
                else:
                    next_break = len(labels)
                if next_break - prev_break < 50:  # Removing this break will not create a sentence of more than 50 tokens
                    labels[i] = 0
            if labels[i] == 1:
                prev_break = i

        if outmode == "binary":
            if as_bound_groups:
                filtered = []
                for idx, lab in enumerate(bg_labels):
                    if lab in ["B","S"]:
                        filtered.append(labels[idx])
                return filtered
            else:
                return labels
        else:
            output = []
            for i, tok in enumerate(toks):
                if labels[i] == 1:
                    pred = "SENT"
                else:
                    pred = "O"
                bg_lab = bg_labels[i]
                output.append("\t".join([tok, pred, bg_lab]))

            return "\n".join(output).strip() + "\n"


if __name__ == "__main__":
    from argparse import ArgumentParser

    p = ArgumentParser()
    p.add_argument("file", nargs='?', help="TT SGML file to test sentence splitting on, or training dir")
    p.add_argument("-m", "--mode", choices=["test", "train", "eval"], default="test")
    p.add_argument(
        "-o",
        "--out_format",
        choices=["binary", "tab"],
        help="output list of binary split indices or TT SGML",
        default="tab",
    )

    opts = p.parse_args()
    sentencer = FlairSentSplitter(train=opts.mode == "train", span_size=20)
    if opts.mode == "train":
        sentencer.train()
    elif opts.mode == "eval":
        data = io.open(opts.file, encoding="utf8").read()
        lines = data.strip().split("\n")
        format = "conllu" if any([l.count("\t") == 9 for l in lines]) else "tt"
        if format == "conllu":
            gold = []
            toks = []
            for line in lines:
                if "\t" in line:
                    fields = line.split("\t")
                    if "." in fields[0] or "-" in fields[0]:
                        continue
                    else:
                        if 'NewSent=Yes' in fields[-1]:
                            gold.append(1)
                        else:
                            gold.append(0)
                        toks.append(fields[1])

        preds = sentencer.predict(data, in_format=format, outmode="binary")
        tp = 0
        fp = 0
        fn = 0
        for i, pred in enumerate(preds):
            if pred == 1:
                if gold[i] == 1:
                    tp += 1
                else:
                    fp += 1
            else:
                if gold[i] == 1:
                    fn += 1
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1 = 2 * (precision * recall) / (precision + recall)
        print(f"Precision: {precision:.2f}, Recall: {recall:.2f}, F1: {f1:.2f}")
        for i,t in enumerate(toks):
            print(t, gold[i], preds[i], sep="\t", end="\n")

    else:
        sgml = io.open(opts.file, encoding="utf8").read()
        result = sentencer.predict(sgml, outmode=opts.out_format)
        print(result)
