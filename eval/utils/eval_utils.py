import tempfile, subprocess
import io, os, sys, re
from six import itervalues
from glob import glob
from itertools import chain

PY3 = sys.version_info[0] == 3

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
eval_dir = script_dir + ".." + os.sep
bohairic_corpora = pub_corpora = "corpora" + os.sep  # Path to clone of CopticScriptorium/corpora

try:
    from fpaths import corpora_dir, ud_dir
except:
    try:
        from .fpaths import corpora_dir, ud_dir
    except:
        # Assume we are running from repo root (e.g. for run_tests.py)
        from eval.utils.fpaths import corpora_dir, ud_dir

# Harvest corpora directory for aliases
aliases = {}


def get_conll_docnames(conllu):
    docs = conllu.split("# newdoc ")[1:]
    docs = [re.search(r"^id = [^\n]+:([^\n]+)", doc).group(1) for doc in docs]
    return docs


def harvest_aliases(harvest_dir, dialect="sahidic"):
    def clean_tb_names(docname):
        docname = docname.replace("1Corinthians", "1Cor")
        docname = docname.replace("MONB_", "")
        docname = re.sub(
            r"([A-Z][A-Z])_([0-9]+)_([0-9]+)$", r"\1\2-\3", docname
        )  # "YA_518_520"->"YA518-520"
        if docname in ["YA421-428", "YA517-518", "YB307-320", "ZC301-308"]:
            docname = "a22." + docname
        return docname

    def get_ud_docs(partition, dialect="sahidic"):
        if dialect == "sahidic":
            conllu = io.open(ud_dir + "cop_scriptorium-ud-" + partition + ".conllu", encoding="utf8").read()
        else:
            conllu = io.open(ud_dir + "cop_bohairic-ud-" + partition + ".conllu", encoding="utf8").read()
        ud_docs = get_conll_docnames(conllu)
        ud_docs = [clean_tb_names(doc) for doc in ud_docs]
        return ud_docs

    global ud_dir

    if dialect == "bohairic":
        ud_dir = ud_dir.replace("UD_Coptic","UD_Bohairic")

    out = {}
    if os.path.exists(harvest_dir):
        corpus_dirs = next(os.walk(harvest_dir))[
            1
        ]  # Immediate children of corpora directory
        for d in corpus_dirs:
            if "treebank" in d:  # Ignore additional treebank directory, since the same docs appear elsewhere
                continue
            if dialect=="bohairic" and "bohairic" not in d:
                continue
            files = glob(corpora_dir + d + os.sep + "*" + os.sep + "*.tt", recursive=True)
            if len(files) > 0:
                out[
                    d.lower()
                ] = files  # Accept GitHub repo directory names, e.g. besa-letters
                out[
                    d.replace("-", ".").lower()
                ] = files  # Accept ANNIS style dot names, e.g. besa.letters
                out[
                    d.replace("life-", "").lower()
                ] = files  # Accept protagonist names, e.g. 'cyrus' for 'life-cyrus'
                out[
                    d.replace("martyrdom-", "").lower()
                ] = files  # Accept protagonist names, e.g. 'victor'
                out[
                    d.replace("shenoute-", "").lower()
                ] = files  # Accept shenoute corpora without shenoute
                out[d.replace("sahidica.", "").lower()] = files
                out[d.replace("sahidic.", "").lower()] = files
                out[d.replace("pseudo-", "").lower()] = files
                for file_ in files:  # Accept individual tt file names
                    out[os.path.basename(file_).replace(".tt", "")] = [file_]

        for partition in ["train", "dev", "test"]:
            docs = get_ud_docs(partition, dialect=dialect)
            if any([a not in out for a in docs]):
                sys.stderr.write(
                    "ERR: Unknown treebank document: "
                    + [a for a in docs if a not in out][0]
                )
                quit()
            out["ud_" + partition] = []
            for a in docs:
                out["ud_" + partition] += out[a]

        all_lists = [l for l in itervalues(out)]
        flat = list(set(list(chain.from_iterable(all_lists))))

        if dialect == "sahidic":
            out["silver_auto"] = [f for f in flat if f not in out["ud_test"]]
            out["gold"] = [f for f in flat if 'segmentation="gold' in io.open(f,encoding="utf8").read() and f not in out["ud_test"] and "bohairic" not in f]
            out["gold_entities"] = [f for f in flat if ' entities="gold' in io.open(f,encoding="utf8").read() and f not in out["ud_test"] and "bohairic" not in f]
            out["checked_entities"] = [f for f in flat if re.search(r' entities="(gold|checked)"',io.open(f,encoding="utf8").read()) is not None and f not in out["ud_test"] and "bohairic" not in f]
            out["silver"] = [f for f in flat if ('segmentation="checked' in io.open(f,encoding="utf8").read() or f in out["gold"]) and f not in out["ud_test"] and "bohairic" not in f]
            out["silver_no_dev"] = [f for f in flat if ('segmentation="checked' in io.open(f,encoding="utf8").read() or f in out["gold"]) and f not in out["ud_dev"] and "bohairic" not in f]
            out["checked_identities"] = [f for f in flat if re.search(r' identities="(gold|checked)"',io.open(f,encoding="utf8").read()) is not None and f not in out["ud_test"] and "bohairic" not in f]
        else:
            out["bohairic_silver_auto"] = [f for f in flat if f not in out["ud_test"] and "bohairic" in f]
            out["bohairic_gold"] = [f for f in flat if 'segmentation="gold' in io.open(f,encoding="utf8").read() and f not in out["ud_test"] and "bohairic" in f]
            #out["bohairic_gold_entities"] = [f for f in flat if ' entities="gold' in io.open(f,encoding="utf8").read() and f not in out["ud_test"] and "bohairic" in f]
            #out["bohairic_checked_entities"] = [f for f in flat if re.search(r' entities="(gold|checked)"',io.open(f,encoding="utf8").read()) is not None and f not in out["ud_test"] and "bohairic" in f]
            out["bohairic_silver"] = [f for f in flat if ('segmentation="checked' in io.open(f,encoding="utf8").read() or f in out["bohairic_gold"]) and f not in out["ud_test"] and "bohairic" in f]
            out["bohairic_silver_tagging"] = [f for f in flat if ('tagging="checked' in io.open(f,encoding="utf8").read() or f in out["bohairic_gold"]) and f not in out["ud_test"] and "bohairic" in f]
            out["bohairic_silver_no_dev"] = [f for f in flat if ('segmentation="checked' in io.open(f,encoding="utf8").read() or f in out["bohairic_gold"]) and f not in out["ud_dev"] and "bohairic" in f]
            #out["bohairic_checked_identities"] = [f for f in flat if re.search(r' identities="(gold|checked)"',io.open(f,encoding="utf8").read()) is not None and f not in out["ud_test"] and "bohairic" in f]

    return out


aliases.update(harvest_aliases(corpora_dir))


def exec_via_temp(input_text, command_params, workdir="", outfile=False):
    temp = tempfile.NamedTemporaryFile(delete=False)
    if outfile:
        temp2 = tempfile.NamedTemporaryFile(delete=False)
    output = ""
    try:
        if input_text is not None:
            temp.write(input_text.encode("utf8"))
            temp.close()

            if outfile:
                command_params = [
                    x
                    if "tempfilename2" not in x
                    else x.replace("tempfilename2", temp2.name)
                    for x in command_params
                ]
            command_params = [
                x if "tempfilename" not in x else x.replace("tempfilename", temp.name)
                for x in command_params
            ]
        if workdir == "":
            proc = subprocess.Popen(
                command_params,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            (stdout, stderr) = proc.communicate()
        else:
            proc = subprocess.Popen(
                command_params,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=workdir,
            )
            (stdout, stderr) = proc.communicate()
        if len(str(stderr)) > 0:
            print(stderr)
        if outfile:
            if PY3:
                output = io.open(temp2.name, encoding="utf8").read()
            else:
                output = open(temp2.name).read()
            temp2.close()
            os.remove(temp2.name)
        else:
            output = stdout
        # print(stderr)
        proc.terminate()
    except Exception as e:
        print(e)
    finally:
        if PY3:
            if not outfile:
                output = output.decode("utf8").replace("\r", "")
        if input_text is not None:
            os.remove(temp.name)
        return output


def list_files(alias="silver", file_dir=None, mode=None, dialect="sahidic"):
    """
	Accept an alias and return a list of file paths. We assume that file_dir is usually the same as corpora_dir,
	which is a clone of CopticScriptorium/corpora. Aliases are auto-lower-cased and can be:

	- An ANNIS corpus name (e.g. besa.letters)
	- A repo corpus folder name (besa-letters)
	- A tt file name without extension (to_aphthonia)
	- An initial substring uniquely identifying a valid option from the above
	- A list of any of the above joined by '+'

	:param alias: alias string, see above
	:param file_dir: directory containing corpus folders with tt files (possibly is recursive sub-folders)
	:param mode: tt, plain_text, plain_bg, parse
	:param dialect: sahidic or bohairic
	:return:
	"""

    global aliases

    if "bohairic" in alias:
        dialect = "bohairic"
    if dialect == "bohairic":
        aliases.update(harvest_aliases(bohairic_corpora, dialect="bohairic"))

    if file_dir is not None:
        aliases.update(harvest_aliases(file_dir, dialect=dialect))

    file_list = []

    if mode is None:
        mode = "tt"

    if "plain" in alias:
        mode = "plain"

    if "+" in alias:
        multiple_aliases = alias.split("+")
        for a in multiple_aliases:
            file_list += list_files(a, file_dir=file_dir, mode=mode, dialect=dialect)
        return list(set(file_list))

    # Resolve substrings
    if "plain" not in mode:
        if alias not in aliases:
            possible_keys = [k for k in aliases if k.startswith(alias)]
            if len(possible_keys) == 1:
                alias = possible_keys[0]
            elif len(possible_keys) > 1:
                shortest = min(possible_keys,key=lambda x:len(x))
                sys.stderr.write("WARN: multiple aliases match '" + alias + "', choosing shortest: " + shortest + "\n")
                alias = shortest
            else:
                sys.stderr.write("ERR: Could not find unambiguous data set alias '" + alias + "'\n")
                sys.exit(0)

    if file_dir is None:
        file_dir = pub_corpora  # Default tt file directory

    if mode == "parse":
        file_dir = eval_dir + "parses" + os.sep
        if alias.lower() == "ud_test":
            file_list = [file_dir + "cop_scriptorium-ud-test.conllu"]
        elif alias.lower() == "ud_train":
            file_list = [file_dir + "cop_scriptorium-ud-train.conllu"]
        elif alias.lower() == "ud_dev_train":
            file_list = [
                file_dir + "cop_scriptorium-ud-train.conllu",
                file_dir + "cop_scriptorium-ud-dev.conllu",
            ]
    elif mode == "plain_text":
        file_dir = eval_dir + "binder_data" + os.sep + "plain" + os.sep
        files = sorted(glob(file_dir + "*.txt"))
        if "-" in alias:
            alias = alias.replace("-","")
            file_list = [f for f in files if alias not in f]
        else:
            file_list = [f for f in files if alias in f]
    elif mode == "plain_bg":
        file_dir = eval_dir + "binder_data" + os.sep + "gold" + os.sep
        files = sorted(glob(file_dir + "*.bg"))
        if "-" in alias:
            alias = alias.replace("-","")
            file_list = [f for f in files if alias not in f]
        else:
            file_list = [f for f in files if alias in f]
    elif mode == "old_plain":
        if alias.lower().startswith("cyrus"):
            file_dir = eval_dir + "plain" + os.sep
            file_list = [file_dir + "BritMusOriental6783_23a_27a.txt"]
        elif alias.lower().startswith("onno"):  # onnophrius
            file_dir = eval_dir + "plain" + os.sep
            file_list = [file_dir + "apa_onnophrius_part1.txt"]
        elif alias.lower().startswith("ephraim"):
            file_dir = eval_dir + "plain" + os.sep
            file_list = [file_dir + "BritMusOriental6783_63b_67b.txt"]
        elif alias.lower().startswith("victor2"):
            file_dir = eval_dir + "plain" + os.sep
            file_list = [file_dir + "martyrdom.victor.02.txt"]
        elif alias.lower().startswith("victor"):
            file_dir = eval_dir + "plain" + os.sep
            file_list = [file_dir + "martyrdom.victor.txt"]
        elif alias.lower().startswith("viccyeph"):
            file_dir = eval_dir + "plain" + os.sep
            file_list = [
                file_dir + "martyrdom.victor.txt",
                file_dir + "BritMusOriental6783_23a_27a.txt",
                file_dir + "BritMusOriental6783_63b_67b.txt",
            ]

        elif alias.lower().startswith("cyephon"):
            file_dir = eval_dir + "plain" + os.sep
            file_list = [
                file_dir + "BritMusOriental6783_23a_27a.txt",
                file_dir + "BritMusOriental6783_63b_67b.txt",
                file_dir + "apa_onnophrius_part1.txt",
            ]
        elif alias.lower().startswith("vicephon"):
            file_dir = eval_dir + "plain" + os.sep
            file_list = [
                file_dir + "martyrdom.victor.txt",
                file_dir + "BritMusOriental6783_63b_67b.txt",
                file_dir + "apa_onnophrius_part1.txt",
            ]
        elif alias.lower().startswith("viccyon"):
            file_dir = eval_dir + "plain" + os.sep
            file_list = [
                file_dir + "martyrdom.victor.txt",
                file_dir + "BritMusOriental6783_23a_27a.txt",
                file_dir + "apa_onnophrius_part1.txt",
            ]
    else:
        alias = alias.lower()
        if alias in aliases:
            return aliases[alias]
        if alias.lower() == "cyrus":
            file_dir = eval_dir + "tt" + os.sep
            file_list = [file_dir + "life.cyrus.01.tt", file_dir + "life.cyrus.02.tt"]
        elif alias.lower().startswith("onno"):  # onnophrius
            file_dir = eval_dir + "unreleased" + os.sep
            file_list = [file_dir + "apa_onnophrius_part1.tt"]
        elif alias.lower().startswith("ephraim"):
            file_dir = eval_dir + "unreleased" + os.sep
            file_list = [file_dir + "BritMusOriental6783_63b_67b.tt"]
        elif alias.lower().startswith("victor2"):
            file_dir = eval_dir + "unreleased" + os.sep
            file_list = [file_dir + "martyrdom.victor.02.tt"]

        #!! DANGER: this is in plain, not unreleased
        elif alias.lower().startswith("victor"):
            file_dir = eval_dir + "plain" + os.sep
            file_list = [file_dir + "martyrdom.victor.01.tt"]

        elif alias.lower() == "ud_test":
            file_list = io.open(eval_dir + "test_list.tab").read().strip().split("\n")
            file_list = [file_dir + f for f in file_list]
        elif alias.lower() == "ud_dev":
            file_list = io.open(eval_dir + "dev_list.tab").read().strip().split("\n")
            file_list = [file_dir + f for f in file_list]
        elif alias.lower() == "ud_train":
            file_list = io.open(eval_dir + "train_list.tab").read().strip().split("\n")
            file_list = [file_dir + f for f in file_list]

        elif alias.lower() == "viccyeph_tt":
            file_dir = eval_dir + "plain" + os.sep
            file_list.append(file_dir + "martyrdom.victor.01.tt")
            file_dir = eval_dir + "unreleased" + os.sep
            file_list = [
                file_dir + "BritMusOriental6783_23a_27a.tt",
                file_dir + "BritMusOriental6783_63b_67b.tt",
            ]
        elif alias.lower() == "cyephon_tt":
            file_dir = eval_dir + "unreleased" + os.sep
            file_list = [
                file_dir + "BritMusOriental6783_23a_27a.tt",
                file_dir + "BritMusOriental6783_63b_67b.tt",
                file_dir + "apa_onnophrius_part1.tt",
            ]
        elif alias.lower() == "vicephon_tt":
            file_dir = eval_dir + "plain" + os.sep
            file_list = [file_dir + "martyrdom.victor.01.tt"]
            file_dir = eval_dir + "unreleased" + os.sep
            file_list += [
                file_dir + "BritMusOriental6783_63b_67b.tt",
                file_dir + "apa_onnophrius_part1.tt",
            ]

        elif alias.lower() == "viccyon_tt":
            file_dir = eval_dir + "plain" + os.sep
            file_list = [file_dir + "martyrdom.victor.01.tt"]
            file_dir = eval_dir + "unreleased" + os.sep
            file_list += [
                file_dir + "BritMusOriental6783_23a_27a.tt",
                file_dir + "apa_onnophrius_part1.tt",
            ]
        elif alias.lower() == "silver":
            sys.stderr.write("WARN: old silver list used at eval_utils.py line 412")
            quit()
            test_list = io.open(eval_dir + "test_list.tab").read().strip().split("\n")
            file_list = glob(file_dir + os.sep + "*.tt")
            filtered = []
            for f in file_list:
                if os.path.basename(f) not in test_list:
                    filtered.append(f)
            file_list = filtered

    return list(set(file_list))  # Return list of unique files


def get_col(data, colnum):
    if not isinstance(data, list):
        data = data.split("\n")

    splits = [row.split("\t") for row in data if "\t" in row]
    return [r[colnum] for r in splits]


def inject_col(source_lines, target_lines, col=-1, into_col=None, skip_supertoks=False):

    output = []
    counter = -1
    target_line = ""

    if not PY3:
        if isinstance(target_lines, unicode):
            target_lines = str(target_lines.encode("utf8"))

    if not isinstance(source_lines, list):
        source_lines = source_lines.split("\n")
    if not isinstance(target_lines, list):
        target_lines = target_lines.split("\n")

    for i, source_line in enumerate(source_lines):
        while len(target_line) == 0:
            counter += 1
            target_line = target_lines[counter]
            if (target_line.startswith("<") and target_line.endswith(">")) or len(
                target_line
            ) == 0:
                output.append(target_line)
                target_line = ""
            else:
                target_cols = target_line.split("\t")
                if "-" in target_cols[0] and skip_supertoks:
                    output.append(target_line)
                    target_line = ""
        source_cols = source_line.split("\t")
        to_inject = source_cols[col]
        target_cols = target_line.split("\t")
        if into_col is None:
            target_cols.append(to_inject)
        else:
            target_cols[into_col] = to_inject
        output.append("\t".join(target_cols))
        target_line = ""

    return "\n".join(output)
