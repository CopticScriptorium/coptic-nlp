# Coptic NLP Pipeline

An end-to-end NLP pipeline for Coptic text in UTF-8 encoding. 

Online production version available as a web interface at:
https://corpling.uis.georgetown.edu/coptic-nlp/

## Requirements

The NLP pipeline can run as a script or as part of the included web interface via a web server (e.g. Apache, using index.py as a landing page).

**Note** you will need TreeTagger and MaltParser 1.8 if you want to use tagging and parsing. The script will offer to attempt to download them if they are missing

## Command line usage

```
usage: python coptic_nlp.py [OPTIONS] files

positional arguments:

  files                 File name or pattern of files to process (e.g. *.txt)

optional arguments:

  -h, --help            show this help message and exit

standard module options:

  -u, --unary           Binarize unary XML milestone tags
  -t, --tag             Do POS tagging
  -l, --lemma           Do lemmatization
  -n, --norm            Do normalization
  -b, --breaklines      Add line tags at line breaks
  -p, --parse           Parse with dependency parser
  -e, --etym            Add etymolgical language of origin for loan words
  -s SENT, --sent SENT  XML tag to split sentences, e.g. verse for <verse ..>
                        (otherwise PUNCT tag is used to split sentences)
  -o {pipes,sgml}, --outmode {pipes,sgml}
                        Output SGML or tokenize with pipes

less common options:
  -f, --finitestate     Use old finite-state tokenizer (less accurate)
  -q, --quiet           Suppress verbose messages
  -x EXTENSION, --extension EXTENSION
                        Extension for SGML mode output files (default: tt)
  --stdout              Print output to stdout, do not create output file
  --para                Add <p> tags if <hi rend="ekthetic"> is present
  --space               Add spaces around punctuation
  --dirout DIROUT       Optional output directory (default: this dir)
  --meta META           Add fixed meta data string read from this file name
  --parse_only          Only add a parse to an existing tagged SGML input
  --no_tok              Do not tokenize at all, input is one token per line
  --pos_spans           Harvest POS tags and lemmas from SGML spans
  --merge_parse         Merge/add a parse into a ready SGML file
  --version             Print version number and quit
```

### Example usage

Add norm, lemma, parse, tag, unary tags and language recognition:
```
> python coptic_nlp.py -penult infile.txt
```

Just tokenize a file using pipes and dashes:
```
> python coptic_nlp.py -o pipes infile.txt
```

Tokenize with pipes and mark up line breaks:
```
> python coptic_nlp.py -b -o pipes infile.txt
```

Normalize, tag, lemmatize and parse, splitting sentences by <verse> tags:
```
> python coptic_nlp.py -pnlt -s verse infile.txt
```

Add full analyses to a whole directory of *.xml files, output to a specified directory:
```
> python coptic_nlp.py -penult --dirout /home/cop/out/ *.xml
```

Parse a tagged SGML file into CoNLL tabular format for treebanking, use translation tag to recognize sentences:
```
> python coptic_nlp.py --no_tok --parse_only --pos_spans -s translation infile.tt
```

Merge a parse into a tagged SGML file's <norm> tags, use translation tag to recognize sentences:
```
> python coptic_nlp.py --merge_parse --pos_spans -s translation infile.tt
```

## Input formats

The pipeline accepts the following kinds of input:

  * Plain text, with bound groups separated by underscores or spaces. 
    * Note that if punctuation has not been separated from bound groups, you can use the `--space` option to attempt to automatically separate punctuation
    * If your Coptic text represents line breaks as new line characters, you can automatically add line break tags using `-b` / `--breaklines`
    * Gold tokenization information may be present in the input at pipes between part-of-speech bearing units and hyphens between morphemes
  * XML/SGML input, with bound groups separated by underscores or spaces. The script will retain XML tags as-is around Coptic text. 
  * Coptic Scriptorium style TreeTagger SGML, with normalized units in tags such as <norm norm="...">. 
    * This input format is used when adding a parse to an existing .tt file using the `--merge_parse` option
    * It is also possible to enrich .tt files with additional annotations, e.g. only add language of origin tags to an existing analysis

### Some example inputs

1. Plain text input, untokenized, no meaningful line breaks, spaces separating bound groups

̀̀̀̀```
Ⲁϥⲥⲱⲧⲙ ⲛϭⲓⲡϣⲃⲏⲣ ⲛ̄ⲧⲙⲛⲧⲁⲧⲥⲱⲧⲙ
```

2. XML input with meaningful line breaks and gold tokenization, underscores separating bound groups

```
Ⲁ|ϥ|ⲥ<hi renf="large">ⲱ</hi>ⲧⲙ_
ⲛϭⲓ|ⲡ|ϣⲃⲏⲣ_ⲛ̄|ⲧ|ⲙⲛⲧ-ⲁ
ⲧ-ⲥⲱⲧⲙ
```

3. TreeTagger SGML input with some analyses, but for example missing the syntactic parse

```
<lb n="1">
<norm_group norm_group="ⲁϥⲥⲱⲧⲙ" orig_group="ⲁϥⲥⲱⲧⲙ">
<norm norm="ⲁ" orig="Ⲁ" lemma="ⲁ" pos="APST">
Ⲁ
</norm>
<norm norm="ϥ" orig="ϥ" lemma="ⲛⲧⲟϥ" pos="PPERS">
ϥ
</norm>
<norm norm="ⲥⲱⲧⲙ" orig="ⲥⲱⲧⲙ" lemma="ⲥⲱⲧⲙ" pos="V">
ⲥ
<hi rend="large">
ⲱ
</hi>
ⲧⲙ
</norm>
</norm_group>
</lb>
<lb n="2">
<norm_group norm_group="ⲛϭⲓⲡϣⲃⲏⲣ" orig_group="ⲛϭⲓⲡϣⲃⲏⲣ">
<norm norm="ⲛϭⲓ" orig="ⲛϭⲓ" lemma="ⲛϭⲓ" pos="PTC">
ⲛϭⲓ
</norm>
<norm norm="ⲡ" orig="ⲡ" lemma="ⲡ" pos="ART">
ⲡ
</norm>
<norm norm="ϣⲃⲏⲣ" orig="ϣⲃⲏⲣ" lemma="ϣⲃⲏⲣ" pos="N">
ϣⲃⲏⲣ
</norm>
</norm_group>
<norm_group norm_group="ⲛⲧⲙⲛⲧⲁⲧⲥⲱⲧⲙ" orig_group="ⲛ̄ⲧⲙⲛⲧⲁⲧⲥⲱⲧⲙ">
<norm norm="ⲛ" orig="ⲛ̄" lemma="ⲛ" pos="PREP">
ⲛ
</norm>
<norm norm="ⲧ" orig="ⲧ" lemma="ⲡ" pos="ART">
ⲧ
</norm>
<norm norm="ⲙⲛⲧⲁⲧⲥⲱⲧⲙ" orig="ⲙⲛⲧⲁⲧⲥⲱⲧⲙ" lemma="ⲙⲛⲧⲁⲧⲥⲱⲧⲙ" pos="N">
<morph morph="ⲙⲛⲧ">
ⲙⲛⲧ
</morph>
<morph morph="ⲁⲧ">
ⲁ
</lb>
<lb n="3">
ⲧ
</morph>
<morph morph="ⲥⲱⲧⲙ">
ⲥⲱⲧⲙ
</morph>
</norm>
</norm_group>
</lb>
```