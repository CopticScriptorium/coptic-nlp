import io
import re
import sys
import os
from argparse import ArgumentParser
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from eval.utils.eval_utils import list_files

# should be the same as in lib/binding/const.py
IGNORE = [
	"",  #	 empty string
	"~",  # U+007E  TILDE
	"`",  # U+0060  GRAVE ACCENT
	"\n",  #	NEWLINE
	"̈",  # U+0308  COMBINING DIAERESIS
	"̄",  # U+0304  COMBINING MACRON
	"̀",  # U+0300  COMBINING GRAVE ACCENT
	"̣",  # U+0323  COMBINING DOT BELOW
	"̅",  # U+0305  COMBINING OVERLINE
	"̂",  # U+0302  COMBINING CIRCUMFLEX ACCENT
	"︤",  # U+FE24  COMBINING MACRON LEFT HALF
	"︥",  # U+FE25  COMBINING MACRON RIGHT HALF
	"︦",  # U+FE26  COMBINING CONJOINING MACRON
	"̇",  # U+0307  COMBINING DOT ABOVE
	"᷍",  # U+1DCD  COMBINING DOUBLE CIRCUMFLEX ABOVE
	"⳿",  # U+2CFF  COPTIC MORPHOLOGICAL DIVIDER
]


def read_and_combine_files(file_list):
    """Given a list of file paths, strip and add a newline character to the contents of each and concatenate them all
    together into a single string.
    :param file_list: a list of file paths
    :return: string contents of all files
    """
    contents = ""
    for f in file_list:
        contents += io.open(f, encoding="utf8").read().strip() + "\n"
    return contents


def main():
    p = ArgumentParser()
    p.add_argument("corpus", default="silver")
    p.add_argument("-n", type=int, default=3)
    opts = p.parse_args()

    file_list = list_files(opts.corpus)
    contents = read_and_combine_files(file_list)

    lines = contents.split("\n")
    gold = []
    for line in lines:
        if "orig_group=" in line:
            grp = re.search('orig_group="([^"]*)"',line).group(1).strip()
            gold.append("".join([c for c in grp.strip() if c not in IGNORE]))

    text = "_".join(gold)

    ngram_before_space = defaultdict(int)
    ngram_not_before_space = defaultdict(int)

    ngram = "#" * opts.n
    for i, c in enumerate(text):
        if c == "_":
            continue

        ngram = ngram[1:] + c
        if i+1 == len(text) or text[i+1] == "_":
            ngram_before_space[ngram] += 1
        else:
            ngram_not_before_space[ngram] += 1

    lines = []
    for k in set(ngram_before_space.keys()).union(ngram_not_before_space.keys()):
        before_space = ngram_before_space[k]
        not_before_space = ngram_not_before_space[k]
        p = float(before_space) / (before_space + not_before_space)
        lines.append((k, before_space, not_before_space, p))

    for line in reversed(sorted(lines, key=lambda x:x[1] * x[3])):
        print("%s\t%s\t%s\t%s" % line)


if __name__ == "__main__":
    main()
