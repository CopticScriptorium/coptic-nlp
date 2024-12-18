#!/usr/bin/python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import sys, io, os, re, tempfile, subprocess
from depedit import DepEdit

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
coptic_nlp_dir = script_dir + ".." + os.sep
bin_dir = script_dir + ".." + os.sep + "bin" + os.sep
data_dir = script_dir + ".." + os.sep + "data" + os.sep

PY3 = sys.version_info[0] == 3


def parse2conllu(parser_output):
    output = []
    for sent in parser_output.sentences:
        toknum = -1
        for position in sorted(list(sent.annotations.keys())):
            fields = sent.annotations[position]
            if "\t" in fields:
                toknum += 1
                fields = fields.split("\t")
                fields[6] = str(sent.values[6][toknum])
                fields[7] = sent.values[7][toknum]
                fields = "\t".join(fields)
            output.append(fields)
        output.append("")
    return "\n".join(output)


def nomisc(conllu):
    output = []
    lines = conllu.split("\n")
    for line in lines:
        if "\t" in line:
            fields = line.split("\t")
            fields[-1] = "_"
            line = "\t".join(fields)
        output.append(line)
    return "\n".join(output)


def exec_via_temp(input_text, command_params, workdir="", input2=None):
    temp = tempfile.NamedTemporaryFile(delete=False)
    exec_out = ""
    try:
        temp.write(input_text.encode("utf8"))
        temp.close()
        temp2 = None

        if any(["tempfilename2" in param for param in command_params]):
            temp2 = tempfile.NamedTemporaryFile(delete=False)
            temp2.write(input2.encode("utf8"))
            temp2.close()
            command_params = [x if 'tempfilename2' not in x else x.replace("tempfilename2",temp2.name) for x in command_params]
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
        if temp2 is not None:
            os.remove(temp2.name)
        if PY3:
            exec_out = exec_out.decode("utf8")
        return exec_out


def run_eval(train_list, test_list, dev_list=None, retrain=True, method="malt", preprocess=False, postprocess=False):

    if preprocess:
        d = DepEdit(config_file=data_dir + "add_ud_and_flat_morph.ini",options=type('', (), {"quiet":True,"kill":"both"})())
    else:
        d = DepEdit(options=type('', (), {"quiet":True,"kill":"both"})())

    train = ""
    for file_ in train_list:
        train += io.open(file_,encoding="utf8").read()

    train = train.split("\n")
    train = d.run_depedit(train)
    train = nomisc(train)

    test_gold = ""
    for file_ in test_list:
        test_gold += io.open(file_,encoding="utf8").read()
    test_gold = d.run_depedit(test_gold)
    test_gold = nomisc(test_gold)

    # Remove supertokens and comments with empty-rule depedit
    d = DepEdit(options=type('', (), {"quiet":True,"kill":"both"})())
    test_gold = d.run_depedit(test_gold.split("\n"))
    test_gold = test_gold.split("\n")

    if dev_list is not None and method != "malt":
        dev_gold = ""
        for file_ in dev_list:
            dev_gold += io.open(file_,encoding="utf8").read()
        dev_gold = d.run_depedit(dev_gold.split("\n"))

    test_blank = []
    for line in test_gold:
        if "\t" in line:
            fields = line.split("\t")
            fields[6:] = ["_","_","_","_"]
        test_blank.append(line)

    test_blank = d.run_depedit(test_blank)

    if method == "malt":
        parser_path = bin_dir + "maltparser-1.8" + os.sep

        if retrain:
            cmd = ["java","-jar","maltparser-1.8.jar","-c","temp","-i","tempfilename",
                   "-F",data_dir+"addMergPOSTAGS0FORMStack0.xml",
                   "-m","learn","-grl","root","-pcr","none","-a","nivrestandard",  # "stacklazy"
                   "-pp","head","-nr",
                   "true","-ne","false"]

            # Train the parser
            exec_via_temp(train,cmd,parser_path)

        # Test
        cmd = ['java','-mx512m','-jar',"maltparser-1.8.jar",'-c','temp','-i','tempfilename','-m','parse']
        parsed = exec_via_temp(test_blank,cmd,parser_path)
        parsed = parsed.replace("\r","")
    elif method == "udpipe":
        parser_path = bin_dir  # Should contain udpipe executable and cop.udpipe

        if retrain:
            # Train the parser
            cmd = [parser_path+"udpipe", "--train", "cop.udpipe","--heldout=tempfilename2","--tagger=none","--tokenizer==none","--transition_system=swap","--embedding_form_file="+parser_path+"cop.vec","tempfilename"]
            exec_via_temp(train,cmd,parser_path,input2=dev_gold)

        # Test
        cmd = [parser_path+'udpipe','--input','conllu','--parse','cop.udpipe','tempfilename']
        parsed = exec_via_temp(test_blank,cmd,parser_path)
        parsed = parsed.replace("\r","")
    elif method == "neural":
        neural_model = coptic_nlp_dir + os.sep + "lib" + os.sep + "cop.diaparser"
        from diaparser.parsers.parser import Parser as NeuralParser
        parser = NeuralParser.load(neural_model)
        parsed = parser.predict(test_blank.strip() + "\n\n")
        parsed = parse2conllu(parsed)

    # Postprocessing
    if postprocess:
        d = DepEdit(config_file=data_dir + "postprocess_parser.ini",options=type('', (), {"quiet":True,"kill":"both"})())
        parsed = d.run_depedit(parsed.split("\n"))

    total=0
    correct_head=0
    correct_label=0
    correct_both=0
    for i, line in enumerate(parsed.strip().split("\n")):
        gold_line = test_gold[i]
        if "\t" in line:
            total +=1
            pred = line.split("\t")
            gold = gold_line.split("\t")
            if gold[6] == pred[6] or (pred[7] == "punct" and gold[7] == "punct"):
                correct_head+=1
            if gold[7] == pred[7]:
                correct_label+=1
            if gold[6:8] == pred[6:8] or (pred[7] == "punct" and gold[7] == "punct"):
                correct_both+=1

    total = float(total)
    acc = correct_both/total
    lab = correct_label/total
    attach = correct_head/total
    print("Label accuracy: " + str(lab))
    print("Attach accuracy: " + str(attach))
    print("LAS: " + str(acc))

    results = {"acc":acc, "lab":lab, "attach":attach}

    with io.open(script_dir + "errors" + os.sep + "parse_pred.conll10",'w',encoding="utf8",newline="\n") as f:
        f.write(parsed)
    with io.open(script_dir + "errors" + os.sep + "parse_gold.conll10",'w',encoding="utf8",newline="\n") as f:
        f.write(nomisc("\n".join(test_gold)))

    return results


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("--train_list",default="ud_train",help="file with one file name per line of conll10 training files or alias such as 'ud_train', 'ud_dev_train'")
    p.add_argument("--test_list",default="ud_test",help="file with one file name per line of conll10 training files or alias such as 'ud_train', 'ud_dev_train'")
    p.add_argument("--dev_list",default="ud_dev",help="file with one file name per line of conll10 training files or alias such as 'ud_dev', 'ud_mini_test")
    p.add_argument("--file_dir",default=None,help="directory with Coptic Treebank files")
    p.add_argument("--method",default="malt",choices=["malt","udpipe","neural"],help="parser to use")
    p.add_argument("--retrain",action="store_true",help="whether to retrain the parser")
    p.add_argument("--preprocess",action="store_true",help="whether to preprocess parser output with depedit")
    p.add_argument("--postprocess",action="store_true",help="whether to postprocess parser output with depedit")

    opts = p.parse_args()

    if opts.file_dir is None:
        file_dir = "UD_Coptic-Scriptorium" + os.sep  # Path to UD_Coptic-Scriptorium clone
    else:
        file_dir = opts.file_dir
        if not file_dir.endswith(os.sep):
            file_dir += os.sep

    if os.path.isfile(opts.test_list):
        test_list = io.open(opts.test_list,encoding="utf8").read().strip().split("\n")
        test_list = [script_dir + opts.file_dir + os.sep + f for f in test_list]
    elif opts.test_list.lower() == "ud_test":
        test_list = [file_dir + "cop_scriptorium-ud-test.conllu"]
    elif opts.test_list.lower() == "ud_dev":
        test_list = [file_dir + "cop_scriptorium-ud-dev.conllu"]
    elif opts.test_list.lower() == "ud_train":
        test_list = [file_dir + "cop_scriptorium-ud-train.conllu"]
    else:
        sys.stderr.write("o Unknown test set: " + str(opts.test_list) + "\n")
        sys.exit(0)

    if os.path.isfile(opts.train_list):
        train_list = io.open(opts.train_list,encoding="utf8").read().strip().split("\n")
        train_list = [file_dir + os.sep + f for f in train_list]
    elif opts.train_list.lower() == "ud_train":
        train_list = [file_dir + "cop_scriptorium-ud-train.conllu"]
    elif opts.train_list.lower() == "ud_dev_train":
        train_list = [file_dir + "cop_scriptorium-ud-train.conllu",file_dir + "cop_scriptorium-ud-dev.conllu"]
    elif opts.train_list.lower() == "ud_dev_test" or opts.train_list.lower() == "ud_dev+ud_test":
        train_list = [file_dir + "cop_scriptorium-ud-test.conllu",file_dir + "cop_scriptorium-ud-dev.conllu"]
    elif opts.train_list.lower() == "ud_train_test" or opts.train_list.lower() == "ud_train+ud_test":
        train_list = [file_dir + "cop_scriptorium-ud-test.conllu",file_dir + "cop_scriptorium-ud-train.conllu"]
    elif opts.train_list.lower() == "ud_all":
        train_list = [file_dir + "cop_scriptorium-ud-test.conllu",file_dir + "cop_scriptorium-ud-train.conllu",file_dir + "cop_scriptorium-ud-dev.conllu"]
    else:
        sys.stderr.write("o Unknown train set: " + str(opts.train_list) + "\n")
        sys.exit(0)

    if os.path.isfile(opts.dev_list):
        dev_list = io.open(opts.dev_list,encoding="utf8").read().strip().split("\n")
        dev_list = [script_dir + opts.file_dir + os.sep + f for f in dev_list]
    elif opts.dev_list.lower() == "ud_test_mini":
        dev_list = [file_dir + "cop_scriptorium-ud-test_mini.conllu"]
    elif opts.dev_list.lower() == "ud_dev":
        dev_list = [file_dir + "cop_scriptorium-ud-dev.conllu"]
    else:
        sys.stderr.write("o Unknown dev set: " + str(opts.dev_list) + "\n")
        sys.exit(0)

    run_eval(train_list, test_list, dev_list=dev_list, method=opts.method, retrain=opts.retrain, preprocess=opts.preprocess, postprocess=opts.postprocess)
