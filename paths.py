import platform

if platform.system() == 'Linux':
	tokenizer_path = '' # Path to tokenize_coptic.pl
	stacked_tok_path = '' # Path to stacked_tokenizer.py
	tt_path = '' # Path to TreeTagger
	lang_path = '' # Path to language of origin script
	milestone_path = '' # Path to binarize_tags.pl
	norm_path = '' # Path to normalizer
	conllize_path = '' # Path to TT2CoNLL.pl
	parser_path = '' # Path to MaltParser
	depedit_path = '' # Path to depedit.py
	python3 = 'python3.5'
else:
	# Alternate paths for running under Windows or Mac
	tokenizer_path = ''
	stacked_tok_path = ''
	tt_path = ''
	lang_path = ''
	milestone_path = ''
	norm_path = ''
	conllize_path = ''
	parser_path = ''
	depedit_path = ''
	python3 = 'python3.5'
