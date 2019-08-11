#!/usr/bin/python
# -*- coding: utf-8 -*-

import io, sys, argparse

"""
Script to evaluate segmentation f-score and perfect super-token segmentation proportion from two files:
 * goldfile: single column file, one super-token perline, pipes denote segmentation positions	
	* predfile: same format
	
Stripped files are assumed to have the same amount of characters except pipes. A super-token may also consist
of a single pipe (i.e. input contained a literal pipe, which must be a complete super-token).
"""


def main(goldfile, predfile, preds_as_string=False,ignore_diff_len=False,replace_diff_len=False,silent=False,sep_only=False):
	lines = io.open(goldfile, encoding="utf8").read().strip().replace("\r", "").split("\n")
	counter = 0
	gold = []
	gold_groups = []
	perfect = 0
	total = 0
	no_sep_lines = set([])

	if "\t" in lines[0]:  # Convenience step allowing 2-column file as gold
		sys.stderr.write("o Found tab in gold file, using second column as gold\n")
		lines = [line.split("\t")[1] for line in lines if "\t" in line]
	for r, line in enumerate(lines):
		total += 1
		if "[" in line or "]" in line and not len(line.strip()) == 1:
			line = line.replace("[","").replace("]","")
		if sep_only and "|" not in line:  # Only evaluate lines that have separator
			no_sep_lines.add(r)
			continue
		gold_groups.append(line.strip())
		for i, c in enumerate(list(line.strip())):
			counter += 1
			if i == len(line.strip()) - 1:  # Last character is trivial, ignore
				continue
			if c == "|":
				if len(line.strip()) > 1 and i == 0:
					print("Complex token begins with boundary marker at gold row " + str(r))
					sys.exit()
				counter -=1
				gold[-1] = 1
			else:
				gold.append(0)

	gold_chars = counter

	if preds_as_string:
		lines = predfile.split("\n")
	else:
		lines = io.open(predfile, encoding="utf8").read().strip().replace("\r", "").split("\n")
	counter = 0
	pred = []
	offset = 0

	for r, line in enumerate(lines):
		# Ignore [ or ] in string
		if "[" in line or "]" in line and not len(line.strip()) == 1:
			line = line.replace("[","").replace("]","")
		if r == len(gold_groups):
			a=4
		if r in no_sep_lines:
			offset -= 1
			continue
		if len(line.replace("|","").strip()) != len(gold_groups[r+offset].replace("|","").strip()):
			# Length mismatch, bug row
			if ignore_diff_len:
				if replace_diff_len:
					line = gold_groups[r+offset].replace("|","").strip()  # Replace prediction with gold length string with no segmentation
				else:
					continue
		if line.strip() == gold_groups[r+offset]:
			perfect += 1
		for i, c in enumerate(list(line.strip())):
			counter += 1
			if i == len(line.strip()) - 1:  # Last character is trivial, ignore
				continue
			if c == "|":
				if len(line.strip()) > 1 and i == 0:
					print("Complex token begins with boundary marker at pred row " + str(r))
					sys.exit()
				counter -=1
				pred[-1] = 1
			else:
				pred.append(0)

	pred_chars = counter

	if pred_chars != gold_chars:
		sys.stderr.write("ERROR: found " + str(gold_chars) + " gold chars but " + str(pred_chars) + " pred chars\n")
		sys.exit()

	true_positive = 0
	false_positive = 0
	false_negative = 0
	for i in range(len(gold)):
		if gold[i] == 0:
			if pred[i] == 0:
				pass
			else:
				false_positive += 1
		else:
			if pred[i] == 0:
				false_negative += 1
			else:
				true_positive += 1

	try:
		precision = true_positive / (float(true_positive) + false_positive)
	except Exception as e:
		precision = 0

	try:
		recall = true_positive / (float(true_positive) + false_negative)
	except Exception as e:
		recall = 0

	try:
		f_score = 2 * (precision * recall) / (precision + recall)
	except:
		f_score = 0

	try:
		perf_score = perfect/float(total)
	except:
		perf_score = 0

	if not silent:
		print("Total chars: " + str(pred_chars))
		print("Perfect groups: " + str(perf_score))
		print("Precision: " + str(precision))
		print("Recall: " + str(recall))
		print("F-Score: " + str(f_score))

	ret_dict = {"chars":pred_chars,"groups":total,"acc":perf_score,"precision": precision,"recall":recall,"f1":f_score}
	return ret_dict


if __name__ == "__main__":
	p = argparse.ArgumentParser()

	p.add_argument("goldfile")
	p.add_argument("predfile")

	opts = p.parse_args()

	main(opts.goldfile,opts.predfile)
