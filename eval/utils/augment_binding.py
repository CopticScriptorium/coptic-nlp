import sys, io, re
from math import floor
from random import random, seed
from eval_utils import list_files

seed(42)

orig_chars = ["̈", "", "̄", "̀", "̣", "`", "̅", "̈", "̂", "︤", "︥", "︦", "⳿", "~", "\n", "[", "]", "̇", "᷍", "⸍"]

breakers = ["ⲉ","ⲉⲧⲃⲉ","ϣⲁ","ⲛⲥⲁ","ⲛ̄ⲥⲁ","ⲛ︦ⲥⲁ","ⲕⲁⲧⲁ","ⲙⲛ","ⲙⲛ︦","ⲙⲛ̄","ϩⲓ","ⲁϫⲛ","ⲁϫⲛ︦","ⲁϫⲛ̄","ⲛⲃⲗ","ⲉⲣⲁⲧ","ϩⲁ","ⲡⲁⲣⲁ","ⲛⲁ","ⲛⲧⲉ","ⲛ̄ⲧⲉ","ⲛ︦ⲧⲉ","ⲛϭⲓ","ϫⲉ","ⲉⲣⲉ","ⲉⲧ"]
breakers += ["ⲙ","ϩⲁⲧⲙ","ϩⲓⲣⲙ","ϩⲙ","ϩⲓⲧⲙ","ϩⲓϫⲙ","ⲉϫⲙ","ⲙ̄","ϩⲁⲧⲙ̄","ϩⲓⲣⲙ̄","ϩⲙ̄","ϩⲓⲧⲙ̄","ϩⲓϫⲙ̄","ⲉϫⲙ̄","ⲙ︦","ϩⲁⲧⲙ︦","ϩⲓⲣⲙ︦","ϩⲙ︦","ϩⲓⲧⲙ︦","ϩⲓϫⲙ︦","ⲉϫⲙ︦"]
breakers += ["ⲛ","ϩⲁⲧⲛ","ϩⲓⲣⲛ","ϩⲛ","ϩⲓⲧⲛ","ϩⲓϫⲛ","ⲉϫⲛ","ϩⲁⲧⲛ̄","ϩⲓⲣⲛ̄","ϩⲛ̄","ϩⲓⲧⲛ̄","ϩⲓϫⲛ̄","ⲉϫⲛ̄","ϩⲁⲧⲛ︦","ϩⲓⲣⲛ︦︦","ϩⲛ︦","ϩⲓⲧⲛ︦","ϩⲓϫⲛ︦","ⲉϫⲛ︦"]
breakers  = ["ⲁ","ⲙⲉ","ⲙⲡ","ⲙ̄ⲡ","ⲙ︦ⲡ","ϣⲁ","ⲙⲉⲣⲉ","ⲙⲡⲉ","ⲙ̄ⲡⲉ","ⲙ︦ⲡⲉ","ϣⲁⲣⲉ","ⲉⲣϣⲁⲛ","ⲟⲩⲛ","ⲟⲩⲛ̄","ⲟⲩⲛ︦"]

pref_breakers = set(breakers)

suf_breakers = ["ϯ","ϫⲓ","ⲣ","ⲣ̄","ⲣ︦"]

always_breakers = ["ϫⲉ","ⲛϭⲓ","ⲛ̄ϭⲓ","ⲛ︦ϭⲓ"]


def clean(text):
	if not text in ["[","]"]:
		for c in orig_chars:
			text = text.replace(c,"")
	return text


def tt2split_groups(tt_string,group_attr="orig_group",unit_attr="orig"):

	output = []
	units = []
	for i,line in enumerate(tt_string.split("\n")):
		if " " + unit_attr + "=" in line:  # new unit
			unit = re.search(" " + unit_attr + '="([^"]*)"',line).group(1).strip()
			if len(unit)>0:
				units.append(unit)
		if "</" + group_attr + ">" in line:  # group ends
			if len(units)>0:
				output.append(units)
				units=[]

	augmented = []
	labels = []
	for units in output:
		bound_group = "".join(units)
		if bound_group == "ϫⲉⲛⲓⲙ":
			a=4
		rnd = random()

		if units[0] in pref_breakers and rnd >0.5 and len(units)>1:
			augmented.append(units[0])
			augmented.append("".join(units[1:]))
			labels.extend([0,1])
			continue

		found=False
		if rnd > 0.5 and len(units)>1:
			for suf in suf_breakers:
				if suf in units[:-1]:
					break_point = units.index(suf)+1
					augmented.append("".join(units[:break_point]))
					augmented.append("".join(units[break_point:]))
					labels.extend([0,1])
					found=True
					break
			if found:
				continue
		found=False
		if len(units)>1:
			for suf in always_breakers:
				if suf in units[:-1]:
					break_point = units.index(suf)+1
					augmented.append("".join(units[:break_point]))
					augmented.append("".join(units[break_point:]))
					labels.extend([0,1])
					found=True
					break
			if found:
				continue


		if rnd <= 0.7:  # normal group
			pass
		elif 0.7 < rnd < 0.9:
			if len(units)>1:
				rnd = random()
				if rnd > 0.8 and len(units)>2:  # Split into three
					augmented.append(units[0])
					augmented.append(units[1])
					augmented.append("".join(units[2:]))
					labels.extend([0,0,1])
				else:  # Split just the first unit
					augmented.append(units[0])
					augmented.append("".join(units[1:]))
					labels.extend([0,1])
				continue
		elif rnd >= 0.9 and len(bound_group)>1:
			rnd = random()
			split_point = floor(len(bound_group)*rnd)
			if len(bound_group) -1 > split_point > 0:
				first = bound_group[:split_point]
				second = bound_group[split_point:]
				augmented.append(first)
				augmented.append(second)
				labels.extend([0,1])
				continue

		# Default case, normal group
		augmented.append("".join(units))
		labels.append(1)

	return augmented, labels


files = list_files("ud_train")

augmented = []
labels = []

for file_ in files:
	m, l = tt2split_groups(io.open(file_,encoding="utf8").read())
	augmented += m
	labels += l

with io.open("aug_bind.txt",'w',encoding="utf8") as f:
	f.write(" ".join(augmented))


gold_groups = []
gold = ""
for i,grp in enumerate(augmented):
	gold += grp
	if labels[i] == 1:
		gold_groups.append(gold)
		gold = ""


with io.open("aug_bind_gold.txt",'w',encoding="utf8") as f:
	for g in gold_groups:
		f.write('<orig_group orig_group="'+g + '">\n</orig_group>\n')


