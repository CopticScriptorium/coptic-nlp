import platform

if platform.system() == 'Linux':
	tokenizer_path = '' # Path to tokenize_coptic.pl
	tt_path = '' # Path to TreeTagger
	lang_path = '' # Path to language of origin script
	milestone_path = '' # Path to binarize_tags.pl
	norm_path = '' # Path to normalizer
	conllize_path = '' # Path to TT2CoNLL.pl
	parser_path = '' # Path to MaltParser
	depedit_path = '' # Path to depedit.py
else:
	# Alternate paths for running under Windows or Mac
	tokenizer_path = ''
	tt_path = ''
	lang_path = ''
	milestone_path = ''
	norm_path = ''
	conllize_path = ''
	parser_path = ''
	depedit_path = ''