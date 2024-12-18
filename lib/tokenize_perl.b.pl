use Getopt::Std;
use utf8;
binmode(STDOUT, ":utf8");
binmode(STDIN, ":utf8");

use File::Basename;
my $dirname = dirname(__FILE__);
$rule_num = 0;

%opts = ();
getopts('r',\%opts) or die $usage;
#help
if ($opts{r}) {
    $rule_nums = 1;
}
else{
$rule_nums = 0;
}

if ($^O eq "MSWin32"){
	$sep = "\\";
}
else{
	$sep = "/";
}

$lexicon =  $dirname . $sep . ".." . $sep . "data.b" .$sep . "copt_lemma_lex.tab";
$segfile  = $dirname . $sep . ".." . $sep . "data.b" .$sep . "segmentation_table.tab";
$morphfile = $dirname . $sep . ".." . $sep . "data.b" .$sep . "morph_table.tab";


### BUILD LEXICON ###
#build function word lists
$pprep = "ⲁϫⲛⲧ|ⲉϩⲣⲁ|ⲉϫⲛⲧⲉ|ⲉϫⲱ|ⲉⲣⲁⲧ|ⲉⲣⲁⲧⲟⲩ|ⲉⲣⲟ|ⲉⲣⲱ(?=ⲧⲉⲛ)|ⲉⲑⲃⲏⲧ|ⲉⲧⲟⲧ|ϩⲁⲉⲓⲁⲧ|ϩⲁϩⲧⲏ|ϩⲁⲣⲁⲧ|ϩⲁⲣⲓϩⲁⲣⲟ|ϩⲁⲣⲟ|ϩⲁⲣⲱ|ϩⲁⲧⲟⲧ|ϩⲓϫⲱ|ϩⲓⲣⲱ|ϩⲓⲧⲉ|ϩⲓⲧⲟⲧ|ϩⲓⲧⲟⲩⲱ|ϩⲓⲱ|ϩⲓⲱⲱ|ⲕⲁⲧⲁⲣⲟ|ⲕⲁⲧⲁⲣⲱ(?=ⲧⲉⲛ)|ⲙⲙⲟ|ⲙⲙⲱ|ⲙⲛⲛⲥⲱ|ⲛⲁ|ⲛϧⲏⲧ|ⲛⲙⲙⲏ|ⲛⲙⲙⲁ|ⲛⲥⲁⲃⲗⲗⲁ|ⲛⲥⲱ|ⲛⲧⲟⲧ|ⲟⲩⲃⲏ|ϣⲁⲣⲟ|ϣⲁⲣⲱ|ⲛ[ⲏⲱ](?=ⲧⲉⲛ)|ⲛⲛⲁϩⲣⲁ|ⲟⲩⲧⲱ|ⲛⲃⲗⲁ|ⲛⲛⲁϩⲣⲏ|ϩⲁⲧⲏ|ⲉⲧⲃⲏⲏ|ⲛⲣⲁⲧ|ⲉⲣⲁ|ⲛⲁϩⲣⲁ|ⲛϩⲏ|ϩⲓⲧⲟⲟ|ⲙⲉⲭⲣⲓ|ⲡⲁⲣⲁⲣⲟ|ⲡⲁⲣⲁⲱ(?=ⲧⲉⲛ)|ⲉⲑⲃⲉ|ⲙⲉⲛⲉⲛⲥⲱ|ⲛⲁϩⲣⲉ?[ⲁⲙⲛ]|ⲛⲧⲁ(?!ⲓ)|ϧⲁⲣⲁⲧ|ⲛⲉⲙⲁ(?=[ϥⲥⲛⲕ])|ⲛⲉⲙⲱ(?=ⲟⲩ)|ⲛⲉⲙⲏ(?=ⲓ)|ⲁⲧϭⲛⲟⲩ";
$pprep .= "|ϧⲉⲛ|ϧⲁϫⲱ|ⲛⲧⲟⲧ|ϩⲓⲱⲧ|ⲉϩⲟⲧⲉⲣⲟ|ⲙⲉⲛⲉⲛⲥⲱ|ⲛⲱ(?=ⲟⲩ)|ⲛⲧⲏ(?=ⲓ)";
$nprep = "ⲉ(?!ⲙⲁⲩ)|ⲛ|ⲙ(?=[ⲡⲃⲙⲫ])|ⲉ[ⲧⲑ]ⲃⲉ|ⲉϩⲣⲉⲛ|ⲉϩⲣⲉⲙ(?=[ⲡⲃⲙⲫ])|ϩⲓⲣⲙ(?=[ⲡⲃⲙⲫ])|ϣⲁ|ⲛⲥⲁ|ⲕⲁⲧⲁ|ⲛⲉⲙ|(?<=^)ⲛⲙ|ϩⲓ|ⲁϫⲉⲛ|ⲛⲧⲉ|ϩⲁⲧⲉⲛ|ϩⲁⲧⲉⲙ(?=[ⲡⲃⲙⲫ])|ϩⲓⲣⲉⲙ(?=[ⲡⲃⲙⲫ])|ϩⲓⲣⲉⲛ|ⲛⲃⲗ|ⲉⲣⲁⲧ|ⲛⲥⲁⲃⲏⲗ|ϩⲓⲧⲉⲛ|ϩⲓⲧⲉⲙ(?=[ⲡⲃⲙⲫ])|ϩⲁ(?!ⲛ)|ⲙⲉⲭⲣⲓ|ⲡⲁⲣⲁ|ⲛⲧⲉ|ⲛ?ⲛⲁϩⲣⲉ?[ⲙⲛ]|ⲉϫⲉⲙ(?=[ⲡⲃⲙⲫ])|ϩⲓϫⲉⲛ|ⲉⲥⲕⲉⲛ|ϩⲓⲥⲕⲉⲛ|ϧⲁ|ϧⲉⲛ|ϧⲁⲧⲉⲛ|ⲛⲧⲉⲛ|ⲛⲉⲙ|ⲉϫⲉⲛ|ⲉϩⲟⲧⲉ|ⲙⲉⲛⲉⲛⲥⲁ|ⲁⲧϭⲛⲉ";
$indprep = "ⲉⲑⲃⲉ|ϧⲉⲛ|ϧⲉⲙ";
$ppers = "ⲓ|ⲕ|ⲭ(?=[ⲃⲗⲙⲛⲣ])|(?<=^ⲛ)ⲅ|ϥ|ⲥ|ⲛ|ⲧⲉⲧⲉⲛ|(?<=(?:ⲙⲡⲉ|ⲉⲧⲉ|ⲁⲣⲉ))ⲧⲉⲛ|(?<=ϣⲁⲧⲉ)ⲧⲉⲛ|(?<=ⲑⲣⲉ)ⲧⲉⲛ|ⲟ?ⲩ|(?<=ⲛ)ⲅ|(?<=^ⲛ)ⲥⲉ";
$ppero = "ⲓ|ⲕ|ϥ|ⲥ|ⲛ|ⲧⲉⲛ|ⲑⲏⲛⲟⲩ|ⲟ?ⲩ|(?<=[ⲉⲟⲩ][ⲱⲟⲩ][ⲗⲩ])ⲧ|(?<=ϣⲟⲡ)ⲧ|(?<=ϩⲙⲉ)ⲧ|(?<=ⲟⲃⲥ)ⲧ|(?<=ⲁϩⲙ)ⲧ|(?<=ⲟⲩϣ)";
$pperinterloc = "ⲁⲛⲅ|ⲛⲧⲕ|ⲛⲧⲉ|ⲁⲛ|ⲁⲛⲟⲛ|ⲛⲧⲉⲧⲉⲛ";
$indpro = 'ⲁⲛⲟⲕ$|ⲛⲑⲟⲕ$|ⲛⲑⲟ$|ⲛⲑⲟⲥ$|ⲛⲑⲟϥ$|ⲁⲛⲟⲛ$|ⲛⲑⲱⲧⲉⲛ$|ⲛⲑⲱⲟⲩ$';
$ke_art = "(?:ⲡⲓ?|ⲧⲓ?|ⲛⲓ?|ⲡⲁⲓ|ⲧⲁⲓ|ⲛⲁⲓ|ⲟⲩ|ϩⲁⲛ)ⲕⲉ";
$femnouns = "ϩⲓⲙⲉ|ⲙⲏⲧⲉ|ϭⲟⲙ|ⲥⲁⲣⲝ|ϩⲉ|ⲉⲡⲓⲥⲧⲟⲗⲏ|ⲉⲕⲕⲗⲏⲥⲓⲁ|ⲙⲉⲧⲟⲩⲣⲟ|ϩⲏ|ⲡⲟⲣⲛⲉⲓⲁ|ⲡⲟⲣⲛⲏ|ⲯⲩⲭⲏ|ⲙⲁⲩ|ⲕⲣⲓⲥⲓⲥ|ϩⲟⲧⲉ|ⲁⲛⲁⲥⲧⲁⲥⲓⲥ|ⲡⲁⲣⲟⲩⲥⲓⲁ|ⲙⲉⲧⲣⲱⲙⲉ|ϫⲓⲛⲱⲛⲁϩ|ⲙⲉⲧⲣⲉϥⲉⲣϩⲟⲧⲉ|ϭⲓⲛⲛⲁⲩ|ϭⲓⲛⲥⲱⲧⲉⲙ|ϭⲓⲛϣⲱⲗⲉⲙ|ϭⲓⲛⲥⲁϫⲓ|ⲉⲛⲉⲣⲅⲓⲁ|ⲕⲟⲗⲁⲥⲓⲥ|ⲩⲛⲟⲩ|ⲧⲁⲡⲣⲟ|ⲡⲟⲗⲓⲥ|ϩⲓⲏ|ⲡⲉ|ⲕⲱⲙⲏ|ⲕⲗⲟⲟⲗⲉ|ⲅⲉⲛⲉⲁ|ⲛⲁⲩ|ⲙⲉⲧⲕⲟⲩⲓ|ⲙⲉⲧⲁⲧⲛⲁϩⲧⲉ|ϭⲓϫ|ⲛⲏⲥⲧⲓⲁ|ⲑⲁⲗⲁⲥⲥⲁ|ⲅⲉϩⲉⲛⲛⲁ|ⲥⲁⲧⲉ|ⲟⲩⲉⲣⲏⲧⲉ|ⲙⲁⲣⲧⲩⲣⲓⲁ|ⲙⲉⲧϫⲱⲱⲣⲉ|ⲟⲩⲱⲧ|ⲏⲡⲉ|ⲥⲏϥⲉ|ⲁⲫⲟⲣⲙⲏ|ⲭⲣⲉⲓⲁ|ϣⲧⲏⲛ|ϣⲉⲉⲣⲉ|ⲩϣⲏ|ⲁⲑⲏⲧ|ⲁⲧⲥⲃⲱ|ⲉⲛⲧⲟⲗⲏ|ⲃⲗⲗⲏ|ⲡⲁϣⲉ|ϩⲉⲛⲉⲉⲧⲏ|ⲥⲩⲛⲁⲅⲱⲅⲏ|ⲙⲉⲧϫⲁⲥⲓϩⲏⲧ|ⲙⲉⲧⲃⲁⲃⲉⲣⲱⲙⲉ|ⲥⲃⲱ|ⲙⲉⲧⲣⲙⲛϩⲏⲧ|ⲡⲁⲛⲟⲩⲣⲅⲓⲁ|ⲙⲉⲧϩⲁⲡⲗⲟⲩⲥ|ⲃⲁϣⲟⲣ|ⲕⲁⲕⲓⲁ|ⲛⲟⲩⲛⲉ|ⲉϩⲉ|ⲁϭⲟⲗⲧⲉ|ⲁⲥⲟⲩ|ⲧⲓⲙⲏ|ϣⲃⲉⲓⲱ|ⲙⲉⲧϩⲏⲕⲉ|ⲙⲉ|ⲙⲉⲧⲁⲑⲏⲧ|ⲟⲓⲕⲟⲩⲙⲉⲛⲏ|ⲙⲉⲧϩⲙϩⲁⲗ|ⲱⲇⲏ|ϩⲉⲗⲡⲓⲥ|ⲭⲁⲣⲓⲥ|ⲉⲓⲣⲏⲛⲏ|ⲙⲉⲧⲙⲛⲧⲣⲉ|ⲕⲟⲓⲛⲱⲛⲓⲁ|ⲥⲟⲫⲓⲁ|ⲙⲉⲧⲥⲁⲃⲉ|ⲙⲉⲧⲥⲟϭ|ⲙⲉⲧϭⲱⲃ|ⲁⲛⲁⲅⲕⲏ|ⲁⲛⲟⲙⲓⲁ|ⲡⲁⲣⲣⲏⲥⲓⲁ|ⲡⲟⲛⲏⲣⲓⲁ|ⲙⲉⲧⲁⲅⲁⲑⲟⲥ|ⲙⲉⲧⲛⲟⲩϯ|ⲙⲉⲧⲁⲧⲛⲟⲩϯ|ⲣⲓ|ⲭⲣⲓⲁ|ⲙⲉⲧⲥⲩⲛⲕⲗⲏⲧⲓⲕⲟⲥ|ⲙⲉⲧⲙⲟⲛⲁⲭⲟⲥ|ⲭⲱⲣⲁ|ⲁⲅⲉⲗⲏ|ϣⲱⲙⲉ|ⲇⲉⲕⲁⲡⲟⲗⲓⲥ|ⲡⲏⲅⲏ|ⲙⲁⲥⲧⲓⲅⲝ|ⲥϩⲓⲙⲉ|ⲡⲓⲥⲧⲓⲥ|ⲉⲝⲟⲩⲥⲓⲁ|ⲁⲡⲉ|ϩⲁⲗⲁⲥⲥⲁ|ⲡⲁⲣⲁⲇⲟⲥⲓⲥ|ⲁⲅⲟⲣⲁ|ⲡⲁⲣⲁⲃⲟⲗⲏ|ⲧⲣⲁⲡⲉⲍⲁ|ⲙⲣⲣⲉ|ⲥⲱϣⲉ|ⲇⲓⲕⲁⲓⲟⲥⲩⲛⲏ|ⲡⲁⲛϩⲟⲡⲗⲓⲁ|ⲁⲅⲁⲡⲏ|ⲙⲉⲧϩⲁⲣϣϩⲏⲧ|ϩⲩⲡⲟⲙⲟⲛⲏ|ⲙⲉⲧⲣⲙⲙⲁⲟ|ⲙⲉⲧⲡⲁⲣⲑⲉⲛⲟⲥ|ⲙⲉⲧϩⲏⲧ|ⲑⲗⲓⲯⲓⲥ|ⲅⲁⲗⲓⲗⲁⲓⲁ|ϩⲓⲉⲣⲟⲩⲥⲁⲗⲏⲙ|ϩⲓⲉⲣⲟⲥⲟⲗⲩⲙⲁ|ⲓⲟⲩⲇⲁⲓⲁ|ⲁⲣⲧⲉⲙⲓⲥ|ⲙⲁⲅⲇⲁⲗⲏⲛⲏ|ⲥⲩⲣⲓⲁ|ⲕⲉⲥⲁⲣⲓⲁ|ⲙⲁⲕⲉⲇⲟⲛⲓⲁ|ⲅⲉϩⲉⲛⲛⲁ|ⲙⲉⲥⲟⲡⲟⲧⲁⲙⲓⲁ|ⲁⲥⲓⲁ|ϩⲉⲕⲁⲧⲏ|ⲁⲭⲁⲓⲁ|ⲅⲁⲗⲁⲧⲓⲁ|ⲡⲉⲧⲣⲁ|ⲡⲉⲛⲧⲏⲕⲟⲥⲧⲏ|ⲧⲣⲓⲁⲥ|ϩⲣⲱⲙⲁⲛⲓⲁ|ⲑⲉⲟⲧⲟⲕⲟⲥ|ⲟⲩⲛⲟⲩ|ⲥⲉⲛϯ";
$mascnouns = "ⲁϥ|ⲓⲱⲧ|ⲥⲱⲙⲁ|ⲡⲛⲉⲩⲙⲁ|ⲣⲉⲛ|ϭⲟⲉⲓⲥ|ϭⲥ|ⲭⲣⲓⲥⲧⲟⲥ|ⲉϩⲟⲟⲩ|ϣⲟⲩϣⲟⲩ|ⲟⲩⲱϣⲙ|ⲡⲁⲥⲭⲁ|ⲕⲟⲥⲙⲟⲥ|ⲛⲟⲩϯ|ⲡⲟⲛⲏⲣⲟⲥ|ⲃⲓⲟⲥ|ⲥⲟⲛ|ⲣⲱⲙⲓ|ⲃⲟⲗ|ⲉⲣⲫⲉⲓ|ⲁϩⲓ|ϣⲏⲣⲓ|ⲙⲁⲓⲣⲱⲙⲓ|ϣⲱⲛⲉⲓⲟⲩϫⲁⲓ|ⲁϣⲁⲓ|ⲛⲟϭⲛⲉϭ|ϣⲓⲡⲓ|ϩⲏⲧ|ϩⲗⲗⲟ|ϫⲡⲓⲟ|ⲙⲉⲩⲓ|ⲙⲁ|ⲙⲧⲟⲛ|ⲙⲟⲧⲓ|ϭⲱⲛⲧ|ϣⲗⲏⲗ|ⲡⲓⲣⲁⲥⲙⲟⲥ|ⲡⲣⲉⲥⲃⲩⲧⲉⲣⲟⲥ|ⲁⲣⲭⲏⲉⲡⲓⲥⲕⲟⲡⲟⲥ|ϩⲟ|ⲥⲁϫⲓ|ϫⲓϩⲣⲁϥ|ⲙⲏϣ|ⲟⲩⲉ|ⲉⲥⲏⲧ|ϫⲟⲉⲓ|ⲱⲃϣ|ⲑⲁⲃ|ⲃⲗⲗⲉ|ⲏⲓ|ⲃⲁⲡⲧⲓⲥⲧⲏⲥ|ⲟⲩⲟⲓ|ⲥⲧⲁⲩⲣⲟⲥ|ⲉⲩⲁⲅⲅⲉⲗⲓⲟⲛ|ⲉⲟⲟⲩ|ⲙⲟⲩ|ⲕⲁϩ|ⲙⲉⲣⲓⲧ|ⲧⲟⲟⲩ|ⲥⲁϩ|ⲕⲱϩⲧ|ⲙⲟⲟⲩ|ⲏⲉⲓ|ⲛⲟϭ|ⲃⲉⲕⲉ|ⲙⲁⲕϩ|ⲱⲛϩ|ⲃⲁⲗ|ϥⲛⲧ|ϩⲙⲟⲩ|ϩⲁⲅⲓⲟⲥ|ⲥⲧⲣⲁⲧⲏⲗⲁⲧⲏⲥ|ⲙⲁⲣⲧⲩⲣⲟⲥ|ϥⲁⲓⲕⲗⲟⲙ|ⲁⲅⲱⲛ|ⲉⲃⲟⲧ|ⲣⲣⲟ|ϣⲟⲣⲡ|ⲇⲓⲁⲃⲟⲗⲟⲥ|ⲙⲧⲟ|ⲥⲉⲡⲓ|ⲣⲟ|ⲡⲁⲗⲗⲁϯⲟⲛ|ⲇⲓⲁⲧⲁⲅⲙⲁ|ϫⲣⲟ|ⲡⲟⲗⲉⲙⲟⲥ|ⲥⲧⲣⲁⲧⲉⲩⲙⲁ|ⲟⲣⲇⲓⲛⲟⲛ|ⲥⲧⲟⲓ|ⲗⲓⲃⲁⲛⲟⲥ|ϣⲟⲩϩⲏⲛⲉ|ϩⲟϫϩϫ|ⲛⲁⲩ|ⲁⲣⲓⲥⲧⲟⲛ|ⲧⲏⲣϥ|ⲙⲁⲕⲁⲣⲓⲟⲥ|ⲧⲃⲃⲟ|ⲅⲉⲛⲛⲁⲓⲟⲥ|ⲥⲁⲃⲃⲁⲧⲟⲛ|ⲕⲟⲙⲉⲥ|ϫⲓⲛϫⲏ|ⲡⲉⲧϩⲟⲟⲩ|ⲡⲉⲧⲛⲁⲛⲟⲩϥ|ⲃⲁⲣⲟⲥ|ϩⲟϥ|ⲡⲁⲣⲁⲇⲉⲓⲥⲟⲥ|ⲃⲟⲏⲑⲟⲥ|ⲥⲧⲉⲣⲉⲱⲙⲁ|ⲥⲟⲫⲟⲥ|ⲣⲙⲛϩⲏⲧ|ⲧⲱⲧ|ⲙⲟⲩⲓ|ⲧⲁⲉⲓⲟ|ⲥⲱϣ|ϣⲃⲣⲣϩⲱⲃ|ⲅⲣⲁⲙⲙⲁⲧⲉⲩⲥ|ϫⲱⲙ|ⲥⲱⲛⲧ|ⲟⲩⲟⲓⲉϣ|ⲱϩⲥ|ⲣⲏ|ⲟⲟϩ|ⲉⲙⲛⲧ|ⲓⲉⲣⲟ|ⲧⲱϩ|ⲟⲩⲱϣ|ⲙⲁⲥⲓ|ϩⲱⲃ|ⲕⲁⲓⲣⲟⲥ|ⲃⲁⲣⲃⲁⲣⲟⲥ|ⲥⲟⲃϯ|ϩⲟ|ⲣⲟⲟⲩϣ|ϩⲟⲩⲟ|ϫⲓⲛϭⲟⲛⲥ|ⲡⲁⲛⲧⲟⲕⲣⲁⲧⲱⲣ|ⲗⲁⲟⲥ|ϩⲁⲣϣϩⲏⲧ|ⲛⲁ|ⲁⲡⲟⲥⲧⲟⲗⲟⲥ|ϭⲱⲗⲡ|ⲧⲁϣⲉⲟⲉⲓϣ|ⲧⲱϩⲙ|ⲡⲛⲉⲩⲙⲁⲧⲓⲕⲟⲥ|ϩⲗⲗⲱ|ⲡⲣⲟⲫⲏⲧⲏⲥ|ϣⲁϥⲉ|ⲟⲩⲟⲉⲓⲛ|ⲕⲁⲕⲉ|ϣⲁϩ|ϩⲏⲃⲥ|ϫⲁϫⲓ|ⲁⲅⲁⲑⲟⲥ|ⲣⲉϥⲉⲣⲛⲟⲃⲓ|ⲁⲧⲛⲟⲩϯ|ⲛⲟⲃⲓ|ⲙⲁⲓⲛⲟⲩϯ|ⲥⲛⲟϥ|ⲙⲟⲛⲁⲭⲟⲥ|ⲕⲣⲟ|ⲟⲩⲱ|ⲁⲣⲭⲓⲥⲩⲛⲁⲅⲱⲅⲟⲥ|ⲁⲙϣⲉ|ϣⲟⲉⲓϣ|ϣⲧⲉⲕⲟ|ϩⲟⲩⲙⲓⲥⲓ|ⲡⲓⲛⲁⲝ|ⲟⲩⲟⲉⲓ|ⲕⲱⲧⲓ|ⲭⲟⲣⲧⲟⲥ|ⲧⲃⲧ|ⲧⲏⲩ|ⲧⲟⲡ|ⲟⲉⲓⲕ|ⲇⲁⲓⲙⲱⲛⲓⲟⲛ|ϭⲗⲟϭ|ⲗⲁⲥ|ⲥⲟⲉⲓⲧ|ⲟⲩⲟⲧⲟⲩⲉⲧ|ϩⲓⲥⲓ|ⲕⲁⲣⲡⲟⲥ|ⲕⲉ|ⲙⲓϣⲓ|ⲥⲙⲟⲧ|ⲧⲱϣ|ϩⲁⲣⲉϩ|ϫⲓⲟⲩⲓ|ϯⲧⲱⲛ|ⲕⲱϩ|ⲙⲟⲥⲧⲓ|ⲕⲣⲟϥ|ϭⲙ|ϣⲓⲛⲓ|ϩⲱⲧ|ϣⲧⲟⲣⲧⲣ|ⲥⲓϯ|ⲛⲉϥ|ⲕⲱϯ|ϩⲓⲱⲓϣ|ⲟⲩⲟϩⲓ|ⲛⲕⲟⲧ|ⲟⲩⲧⲁϩ|ⲟⲥϧ|ⲱⲥϧ|ⲙⲟϩ|ϧⲓⲥⲓ|ⲧⲟⲓ|ⲕⲱⲧ|ⲙⲁϩⲓ";
$mascnouns .= "|ϩⲃⲏⲩⲉ";  # Plurals
$femnouns .= "|ϩⲃⲏⲩⲉ";  # Plurals
$nofemnouns = "(?!(?:" . $femnouns .")\$)";
$nomascnouns = "(?!(?:" . $mascnouns .")\$)";
$possnoun = "ⲣⲱ|ⲣⲁⲧ|ϩⲑⲏ|ⲣⲉⲛ";

$art = "ⲡⲓ?" . $nofemnouns . "|ⲡⲉ(?=(?:[^ⲁⲉⲓⲟⲩⲏⲱ][^ⲁⲉⲓⲟⲩⲏⲱ]|ⲯ|ⲭ|ⲑ|ⲫ|ⲝ|ϩⲟⲟⲩ|ⲟ?ⲩⲟⲉⲓϣ|ⲣⲟⲙⲡⲉ|ⲟ?ⲩϣⲏ|ⲟ?ⲩⲛⲟⲩ))|ⲛ|ⲛⲉ(?=(?:[^ⲁⲉⲓⲟⲩⲏⲱ][^ⲁⲉⲓⲟⲩⲏⲱ]|ⲯ|ⲭ|ⲑ|ⲫ|ⲝ|ϩⲟⲟⲩ|ⲟ?ⲩⲟⲉⲓϣ|ⲣⲟⲙⲡⲉ|ⲟ?ⲩϣⲏ|ⲟ?ⲩⲛⲟⲩ))|ⲧ".$nomascnouns."|ⲧⲉ(?=(?:[^ⲁⲉⲓⲟⲩⲏⲱ][^ⲁⲉⲓⲟⲩⲏⲱ]|ⲯ|ⲭ|ⲑ|ⲫ|ⲝ|ϩⲟⲟⲩ|ⲟ?ⲩⲟⲉⲓϣ|ⲣⲟⲙⲡⲉ|ⲟ?ⲩϣⲏ|ⲟ?ⲩⲛⲟⲩ))|ⲟⲩ|(?<=[ⲁⲉ])ⲩ|ϩⲁⲛ|[ⲡⲫ]ⲁⲓ".$nofemnouns."|[ⲧⲑ]ⲁⲓ".$nomascnouns."|ⲛⲁⲓ|ⲕⲉ|ⲙ(?=[ⲙⲡⲃ])";
$art = $art . "|" . $ke_art . "|" . "ⲛⲓ|ϯ". $nomascnouns ."|ⲫ(?=[ⲃⲗⲙⲛⲣ])|ⲑ(?=[ⲃⲗⲙⲛⲣ])|ⲫ(?=ⲓⲟⲙ)";
$ppos = "ⲡ(?:ⲉ(?:[ⲕϥⲥⲛⲩ]|ⲧⲉⲛ)|ⲁ|ⲟⲩ)".$nofemnouns."|ⲧ(?:ⲉ(?:[ⲕϥⲥⲛⲩ]|ⲧⲉⲛ)|ⲁ|ⲟⲩ)".$nomascnouns."|ⲛ(?:ⲉ(?:[ⲕϥⲥⲛⲩ]|ⲧⲉⲛ)|ⲁ|ⲟⲩ)";
# note Bohairic 2pl. past a-teten, var. are-ten
$ppossub = "ⲫⲱϥ|ⲑⲱϥ|ⲛⲟⲩϥ|ⲫⲱⲓ|ⲑⲱⲓ|ⲛⲟⲩⲓ|ⲫⲱⲕ|ⲑⲱⲕ|ⲛⲟⲩⲕ|ⲫⲱⲧⲉⲛ|ⲑⲱⲧⲉⲛ|ⲛⲟⲩⲧⲉⲛ";
$triprobase = "ⲁ(?:ⲣⲉ(?=ⲧⲉⲛ))?|ⲙⲡ[ⲁⲉ]?|ϣⲁ|ⲙⲉ|ⲙⲡⲁⲧ|ϣⲁⲧⲉ?|ⲛⲛⲉ|ⲛⲧⲉ|ⲛⲧ(?=ⲟⲩ)|ⲛ(?=(?:ⲧⲁ|ⲅ|ϥ|ⲧⲛ|ⲧⲉⲧⲛ|ⲥⲉ))|ⲑⲣⲉ|ⲧⲁⲣⲉ?|ⲙⲁⲣⲉ?|ⲙⲡⲉⲣⲑⲣⲉ"; 
$trinbase = "ⲁ|ⲙⲡⲉ|ⲙⲡⲁⲣⲉ|ϣⲁⲣⲉ|ⲙⲉⲣⲉ|ⲙⲡⲁⲧⲉ|ϣⲁⲧⲉ|ⲛⲛⲉ|ⲛⲧⲉ|ⲑⲣⲉ|ⲧⲁⲣⲉ|ⲙⲁⲣⲉ|ⲙⲡⲉⲛⲑⲣⲉ|ⲁⲣⲉϣⲁⲛ";
$bibase = "ϯ|ⲧⲉ|ⲕ|(?<=ⲛ)ⲅ|ϥ|ⲥ|ⲧⲉⲛ|ⲧⲉⲧⲉⲛ|ⲧⲉⲧ(?=ⲛⲁ.)|ⲥⲉ";
$exist = "ⲟⲩⲟⲛ|ⲙⲙⲟⲛ";

$eth = "ⲉ(?:ⲧ|ⲑ(?=[ⲃⲗⲙⲛⲣ]))";  # Short relative and allomorph with theta

@intransitive = ("ϯϩⲉ","ⲛⲟⲩ","ⲃⲱⲕ","ⲙⲟⲟϣⲉ","ⲉⲓ","ⲓ","ϣⲱⲡⲉ","ⲥⲱⲧⲉⲙ","ⲛⲁⲩ","ⲥⲁϫⲓ","ⲙⲟⲩ","ϣⲗⲏⲗ","ϩⲉⲙⲥⲓ","ϣⲉ","ⲉⲓⲏ","ⲉⲓⲱ","ⲛⲁⲓ");
@transitive = ("ⲕⲟⲥ","ϣⲟⲩⲱ","ⲕⲟⲧ");
@finalnouns = ('ⲣⲟ', 'ⲧⲁϥ', 'ϣⲃⲱ', 'ⲧⲟ', 'ⲣⲏ');

#get external open class lexicon
if ($lexicon ne "")
{
open LEX,"<:encoding(UTF-8)",$lexicon or die "could not find lexicon file $lexicon";
while (<LEX>) {
    chomp;
	if ($_ =~ /^(.*)\t(.*)\t(.*)$/) #ignore comments in modifier file marked by #
    {
	if ($1 =~ '\[\.\.\]'){} # Ignore [..] to avoid error "POSIX syntax[..] is reserved for future extensions in regex"
	elsif ($2 eq 'N') {
		$temp_noun = $1;
		if ($temp_noun eq 'ⲟⲟⲩ'){$temp_noun = '(?<=ⲡ)ⲟⲟⲩ';}  # this form always preceded by article
		elsif ($temp_noun eq 'ⲟⲩⲉ'){$temp_noun = '(?<=[ⲡⲛ])ⲟⲩⲉ';}  # this form always preceded by article or prepositional n-
		elsif ($temp_noun ~~ @finalnouns){$temp_noun .= '$';} # must be group final
		elsif ($temp_noun eq 'ⲥⲧⲟⲗⲏ' || $temp_noun eq 'ⲥⲕⲟⲡⲟⲥ'){$temp_noun = '(?<!ⲉⲡⲓ)' . $temp_noun;}
		elsif ($temp_noun eq 'ⲁⲣⲝ'){$temp_noun = '(?<!ⲥ)' . $temp_noun;}  # Prevent ⲛ|ⲧⲉⲥ|ⲁⲣⲝ and similar
		$nounlist .= "$temp_noun|";
	} 
	elsif ($2 eq 'NPROP' || $2 eq 'N_PPERO') {$namelist .= "$1|";}  # note N_PPERO is definite, so it behaves like a name
	elsif ($2 eq 'NUM') { # numbers must be bound group final, also act like 'names' in that they can appear without articles
		if (length($1) > 1){$nounlist .= "$1" . '$|'; }  # single char = letters used as numbers, don't behave like nouns
		$namelist .= "$1" . '$|';
	}  
	elsif ($2 eq 'V' || $2 eq 'VIMP') {
			if ($1 eq 'ⲉⲛ' || $1 eq 'ⲛ'){  # special handlers for unusual/overgenerating verbs
				$verblist .= "$1(?=[^\s])|";
			}
			elsif ($1 eq 'ⲛⲧ' || $1 eq 'ϣ' || $1 eq 'ⲉϣ'){  # special handlers for unusual/overgenerating verbs
				$verblist .= "$1(?=$ppero)$|";
			}
			elsif ($1 eq 'ⲉⲣ'){
				$verblist .= "(?<=[^ⲥ])$1|";  # must be non initial (otherwise it's infinitive with ⲉ-) and not after ⲥ- (ⲥⲣ- is a form of ⲥⲱⲣ)
			}
			elsif ($2 eq 'V'){
				$temp_verb = $1;
				if ($temp_verb ~~ @intransitive){
					$temp_verb .= '$';
				}elsif ($temp_verb ~~ @transitive){
					$temp_verb .= '(?=[^\s])';
				}
				$verblist .= "$temp_verb|ϣϫⲉⲙϫⲟⲙ|";
			}
			if ($2 eq 'VIMP'){
				$vimplist .= "$1|";
			}
		} 
	elsif ($2 eq 'VSTAT') {$vstatlist .= "$1|";} 
	elsif ($2 eq 'ADV') {$advlist .= "$1|";} 
	elsif ($2 eq 'VBD') {$vbdlist .= "$1|";} 
	elsif ($2 eq 'IMOD') {$imodlist .= "$1|";} 
	elsif ($2 ne 'N' && $1 ne 'ⲙⲙⲟⲛ') {$stoplist{$1} = "$1;$2";} 
	}
}


#add ad hoc stoplist members
$stoplist{'ϥⲓ'} = 'ϥⲓ;V';

#add negated TM forms of verbs
$tm = $verblist;
$tm =~ s/\|/|ϣⲧⲉⲙ/g;
$verblist .=  "$tm";
$verblist .=  "|ⲙⲉϣϣⲉ";

#add noun derivations
$at = $verblist;
$at =~ s/\|/|(?:(?:ⲙⲉⲧ)?ⲁⲧ|ⲣⲉϥ|ⲙⲉⲧ)/g;
$nounlist .=  "$at";
$art_names = "ϩⲓⲉⲣⲟⲥⲟⲗⲩⲙⲁ|ⲓⲉⲣⲟⲥⲁⲗⲏⲙ|ⲅⲁⲗⲓⲗⲁⲓⲁ|ϩⲓⲉⲣⲟⲩⲥⲁⲗⲏⲙ|ⲓⲟⲩⲇⲁⲓⲁ|ⲥⲓⲇⲱⲛ|ϩⲩⲇⲟⲩⲙⲉⲁ|ⲏⲣⲱⲇⲓⲁⲛⲟⲥ|ⲓⲟⲩⲇⲉⲁ|ⲁⲣⲧⲉⲙⲓⲥ|ⲙⲁⲅⲇⲁⲗⲏⲛⲏ|ⲥⲩⲣⲓⲁ|ⲕⲉⲥⲁⲣⲓⲁ|ⲙⲁⲕⲉⲇⲟⲛⲓⲁ|ⲅⲉϩⲉⲛⲛⲁ|ⲙⲉⲥⲟⲡⲟⲧⲁⲙⲓⲁ|ⲁⲥⲓⲁ|ϩⲉⲕⲁⲧⲏ|ⲁⲭⲁⲓⲁ|ⲅⲁⲗⲁⲧⲓⲁ|ⲡⲉⲧⲣⲁ|ⲡⲉⲛⲧⲏⲕⲟⲥⲧⲏ|ⲧⲣⲓⲁⲥ|ϩⲣⲱⲙⲁⲛⲓⲁ|ⲫⲓⲗⲓⲡⲡⲟⲥ|ⲑⲉⲟⲧⲟⲕⲟⲥ|ⲭⲣⲓⲥⲧⲓⲁⲛⲟⲥ|ⲁⲣⲧⲉⲙⲓⲥ|ⲛⲁⲩⲏ|ϩⲏⲗⲉⲓⲁⲥ|ⲡⲁⲣⲙⲟⲩⲧⲉ|ⲓⲟⲩⲇⲁⲓ|ⲧⲁⲣⲧⲁⲣⲟⲥ|ⲁⲙⲟⲣⲣⲁⲓⲟⲥ|ⲁⲙⲛⲧⲉ|ⲕⲁⲉⲓⲛ|ⲉⲫⲣⲁⲑⲁ|ⲥⲁⲇⲇⲟⲩⲕⲁⲓⲟⲥ|ⲥⲩⲛϩⲉⲇⲣⲓⲟⲛ|ⲅⲉⲣⲁⲥⲏⲛⲟⲥ|ⲫⲩⲗⲓⲥⲧⲉⲓⲙ|ⲫⲁⲣⲓⲥⲥⲁⲓⲟⲥ|ⲥⲁⲧⲁⲛⲁⲥ|ⲓⲥⲣⲁⲏⲗ|ⲁⲡⲟⲗⲗⲱⲛ|ⲓⲟⲣⲇⲁⲛⲏⲥ|ⲇⲓⲁⲃⲟⲗⲟⲥ|ⲓⲟⲩⲇⲁⲓ|ϩⲉⲛⲁⲧⲟⲛ|ⲙⲁⲙⲙⲱⲛⲁⲥ|ⲥⲩⲛϩⲉⲇⲣⲓⲟⲛ|ⲛⲁⲍⲁⲣⲏⲛⲟⲥ|ⲉⲕⲗⲏⲥⲓⲁⲥⲧⲏⲥ|ⲛⲟⲏ|ϩⲉⲣⲙⲏⲥ|ⲓⲥⲕⲁⲣⲓⲱⲧⲏⲥ|ⲧⲁⲣⲧⲁⲣⲟⲥ|ⲁⲙⲁⲗⲉⲕ|ⲑⲉⲥⲃⲓⲧⲏⲥ|ⲓⲟⲣⲇⲁⲛⲏⲥ|ⲗⲩⲕⲓⲁ|ⲁⲙⲁⲗⲏⲕ|ⲁⲙⲁⲗⲉⲕ|ⲕⲁⲛⲁⲛⲉⲟⲥ";
$nounlist .="$art_names|%%%";
$verb_or_imp_list = $verblist;
$verb_or_imp_list .= $vimplist . "%%%";
$verblist .="%%%";
$vstatlist .="%%%";
$advlist .="%%%";
$namelist_pure = $namelist;
$namelist .= $indpro . '|ϩⲗⲓ$';
$namelist .='|ⲫⲏ|ⲑⲏ|ⲛⲏ|ϭⲉ|ϩⲓⲟⲛⲉ|ⲛⲓⲙ|ⲟⲩ|ϩⲗⲓ$|ⲟⲩⲟⲛ$|ⲟⲩⲁⲓ$|%%%';
$namelist_pure .= "|ⲫⲏ|ⲑⲏ|ⲛⲏ|ϭⲉ|ϩⲓⲟⲛⲉ|ⲛⲓⲙ|ⲟⲩ|ⲗⲁⲁⲩ|%%%";
$vimplist .= "%%%";
}
### END LEXICON ###

### PREVIOUS SEGMENTATIONS ###
#get most frequent previous segmentations from training corpus
if ($segfile ne "")
{
open SEG,"<:encoding(UTF-8)",$segfile or die "could not find segmentation file";
while (<SEG>) {
    chomp;
	if ($_ =~ /^(.*)\t(.*)$/)
    {
		$segs{$1} = $2;
	}
}
}

# Fixed segs
$segs{"ⲛⲉⲙⲁϥ"} = "ⲛⲉⲙⲁ|ϥ";
$segs{"ϫⲉⲟⲩⲁ"} = "ϫⲉⲟⲩⲁ";
$segs{"ⲉⲓ"} = "ⲉ|ⲓ";

#get most frequent previous morphological analyses from training corpus
if ($morphfile ne "")
{
open MORPH,"<:encoding(UTF-8)",$morphfile or die "could not find segmentation file";
while (<MORPH>) {
    chomp;
	if ($_ =~ /^(.*)\t(.*)$/)
    {
		$morphs{$1} = $2;
	}
}
}
### END PREVIOUS SEGMENTATIONS ###

## MAIN LOOP ###
open FILE,"<:encoding(UTF-8)",shift or die "could not find input document";

while (<FILE>){
	chomp;
	$line = $_;
	$line =~ s/[\n\r]+//g;
	if ($rule_nums){
	    @res = &tokenize($line);
	    $res = $res[0] . "\t" . $res[1];
	}
	else{
	    $res = &tokenize($line);
	}
	$res =~ s/ϣϫⲉⲙϫⲟⲙ/ϣ|ϫⲉⲙϫⲟⲙ/;
	print $res . "\n";
}


sub tokenize{
	$strWord = $_[0];
	$rule_num = 0;
		
			#Activate?
			#if ($strWord =~ m/ⲑ\|/ && $trust_tokenization == 1) {
			#	$strWord =~ s/\|//g;
			#}

			#check for theta/phi containing an article
			if(++$rule_num && $strWord =~ /^($nprep|$pprep)?(ⲑ|ⲫ)(.+)$/o && 0) # DISABLED
			{
				if (defined($1)){$opt_prep = $1;}else{$opt_prep="";}
				$theta_phi = $2;
				$noun_candidate = $3;
				$noun_candidate =  "ϩ" . $noun_candidate;
				if ($noun_candidate =~ /^($nounlist|$namelist)$/o) #experimentally allowing proper nouns with articles
				{
					if ($theta_phi eq "ⲑ") {$theta_phi = "ⲧ";} else {$theta_phi = "ⲡ";}
					$strWord = $opt_prep . $theta_phi . $noun_candidate;
				}
			}
			#check for theta containing a relative converter
			
			if(++$rule_num && $strWord =~ /^((?:(?:$nprep|$pprep)?$art)?ⲉⲑ)(.+)$/o && 0) # DISABLED
			{
				$theta= $1;
				$verb_candidate = $2;
				$theta=~s/ⲑ$/ⲧ/;
				$verb_candidate =  "ϩ" .  $verb_candidate;
				if ($verb_candidate =~ /^($verblist|$vstatlist)$/o) 
				{
					$strWord = $theta . $verb_candidate;
				}
			}

			#check for fused t-i
			if(++$rule_num && $strWord =~ /^(ϣⲁⲛ|ⲙⲡⲁ)ϯ(.*)/)
			{
				$candidate = $1;
				$candidate .=  "ⲧ";
				if (defined($2)){$ending = $2;}else{$ending="";}
				if ($candidate =~ /^($triprobase|$pprep)$/o) 
				{
					$strWord = $candidate . "ⲓ". $ending;
				}
			}
			elsif(++$rule_num && $strWord =~ /^(.*)ϯ(.+)$/)
			{
				$candidate = $2;
				$candidate =  "ⲓ" . $candidate;
				if (defined($1)){$start = $1;}else{$start="";}
				if ($candidate =~ /^($nounlist|$namelist)$/o) 
				{
					$strWord = $start . "ⲧ". $candidate;
				}
			}
			
			#get diagnostics on word shape to rule out some time consuming checks
			$et_ = (&begins_with($strWord, "ⲉⲧ") || &begins_with($strWord, "ⲉⲑ"));
			$je_ = &begins_with($strWord, "ϫⲉ");
			$mns_ = &begins_with($strWord, "ⲙⲉⲛⲉⲛⲥⲁ");
			$ant_ = &begins_with($strWord, "ⲁⲛⲧⲓ");
			$hn_ = $strWord =~ m/^$nprep/o;
			$_f = $strWord =~ m/$ppero$/o;
			$tri_ = ($strWord =~ m/$triprobase/o || &begins_with($strWord, "ⲁⲣⲉϣⲁⲛ"));
			
			#adhoc segmentations
			if (++$rule_num && $strWord eq "ⲛⲁⲩ"){$strWord = "ⲛⲁ|ⲩ";} #free standing nau is a PP not a V
			elsif (++$rule_num && $strWord eq "ⲛⲁϣ"){$strWord = "ⲛ|ⲁϣ";} #"in which (way)"
			elsif (++$rule_num && $strWord eq "ⲉⲓⲣⲉ"){$strWord = "ⲉⲓⲣⲉ";} #free standing eire is not e|i|re
			elsif (++$rule_num && $strWord eq "ϩⲟⲡⲟⲩ"){$strWord = "ϩⲟⲡⲟⲩ";} #free standing hopou is not hop|ou
			elsif (++$rule_num && $strWord eq "ⲉϫⲓ"){$strWord = "ⲉ|ϫⲓ";}
			elsif (++$rule_num && $strWord eq "ⲛⲏⲧⲛ"){$strWord = "ⲛⲏ|ⲧⲛ";}

			#check stoplist
			elsif (++$rule_num && exists $stoplist{$strWord}) {$strWord = $strWord;}

			#check segmentation file
			elsif (++$rule_num && exists $segs{$strWord}) {$strWord = $segs{$strWord};}
			
			#adverbs
			elsif (++$rule_num && $strWord =~ /^($advlist)$/){$strWord = $1;}
			
			#optative/conditional, make ppers a portmanteau segment with base
			elsif (++$rule_num && $strWord =~ /^(ⲉ(?:$ppers)ⲉ|ⲁ(?:$ppers)ϣⲁⲛ)($verblist)$/o) {$strWord = $1 . "|" . $2;}
			elsif (++$rule_num && $strWord =~ /^(ⲉ(?:$ppers)ⲉ|ⲁ(?:$ppers)ϣⲁⲛ)($verblist)($ppero|$namelist)$/o) {$strWord = $1 . "|" . $2."|" . $3;}  #COMPOUND: $nounlist
			elsif (++$rule_num && $strWord =~ /^(ⲉ(?:$ppers)ⲉ|ⲁ(?:$ppers)ϣⲁⲛ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2."|" . $3."|" . $4;}
			# with je / et
			elsif (++$rule_num && ($je_ || $et_) && $strWord =~ /^(ϫⲉ|ⲉⲧ)(ⲉ(?:$ppers)ⲉ|ⲁ(?:$ppers)ϣⲁⲛ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && ($je_ || $et_) && $strWord =~ /^(ϫⲉ|ⲉⲧ)(ⲉ(?:$ppers)ⲉ|ⲁ(?:$ppers)ϣⲁⲛ)($verblist)($ppero|$namelist)$/o) {$strWord = $1."|" . $2 . "|" . $3. "|" . $4;}  #COMPOUND: $nounlist
			elsif (++$rule_num && ($je_ || $et_) && $strWord =~ /^(ϫⲉ|ⲉⲧ)(ⲉ(?:$ppers)ⲉ|ⲁ(?:$ppers)ϣⲁⲛ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 ."|" . $2 ."|" . $3."|" . $4 . "|" .$5;}
			
			#ⲧⲏⲣ=
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲧⲏⲣ)($ppero)$/){$strWord = $1 ."|" . $2;}

			#pure existential
			elsif (++$rule_num && $strWord =~ /^(ⲟⲩⲟⲛ|ⲙⲙⲟⲛ)($nounlist)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif (++$rule_num && $strWord =~ /^(ϫⲉ)(ⲟⲩⲟⲛ|ⲙⲙⲟⲛ)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}

			#tre- causative infinitives
			elsif(++$rule_num && $strWord =~ /^($triprobase)($ppers)(ⲑⲣⲉ|ⲑⲣ(?=ⲟⲩ)|ⲑⲣ(?=ⲁ))($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲉⲛⲉⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲑⲣⲉ)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $_f && $strWord =~ /^(ⲉ|ⲙⲉⲛⲉⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲑⲣⲉ)($ppers)($verblist)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲉⲛⲉⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲑⲣ)(ⲁ|ⲟⲩ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $_f && $strWord =~ /^(ⲉ|ⲙⲉⲛⲉⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲑⲣ)(ⲁ|ⲟⲩ)($verblist)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲉⲛⲉⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲑⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲉⲛⲉⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲑⲣⲉ)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲉⲛⲉⲛⲥⲁ|ⲁⲛⲧⲓ)(ϣⲧⲉⲙ)(ⲑⲣⲉ)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $_f && $strWord =~ /^(ⲉ|ⲙⲉⲛⲉⲛⲥⲁ|ⲁⲛⲧⲓ)(ϣⲧⲉⲙ)(ⲑⲣⲉ)($ppers)($verblist)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲉⲛⲉⲛⲥⲁ|ⲁⲛⲧⲓ)(ϣⲧⲉⲙ)(ⲑⲣ)(ⲁ|ⲟⲩ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $_f && $strWord =~ /^(ⲉ|ⲙⲉⲛⲉⲛⲥⲁ|ⲁⲛⲧⲓ)(ϣⲧⲉⲙ)(ⲑⲣ)(ⲁ|ⲟⲩ)($verblist)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲉⲛⲉⲛⲥⲁ|ⲁⲛⲧⲓ)(ϣⲧⲉⲙ)(ⲑⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲉⲛⲉⲛⲥⲁ|ⲁⲛⲧⲓ)(ϣⲧⲉⲙ)(ⲑⲣⲉ)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif(++$rule_num && $et_ && $strWord =~ /^(ⲉⲑ)(ⲛⲁ)(ⲑⲣⲉ)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif(++$rule_num && $et_ && $strWord =~ /^(ⲉⲑ)(ⲛⲁ)(ⲑⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			
			#prepositions
			elsif (++$rule_num && $_f && $strWord =~ /^($pprep)($ppero)$/){$strWord = $1 . "|" . $2;}
			elsif (++$rule_num && $hn_ && $strWord =~ /^($nprep)($namelist_pure)$/){$strWord = $1 . "|" . $2;}
			elsif (++$rule_num && $hn_ && $strWord =~ /^($nprep)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;} #experimentally allowing proper nouns with articles
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)($pprep)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($nprep)($namelist)$/){$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($nprep)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;} #experimentally allowing proper nouns with articles
			#elsif ($strWord =~ /^($nprep)($art|$ppos)ⲉ($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}

			#elsif ($strWord =~ /^($art|$ppos)($namelist)$/o) {$strWord = $1 . "|" . $2 ;} #experimental, allow names with article
			#relative generic NP p-et-o, ... 
			elsif (++$rule_num && $et_ && $strWord =~ /^($eth)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif (++$rule_num && $strWord =~ /^($art)($eth)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $_f && $strWord =~ /^($art)($eth)($pprep)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $_f && $et_ && $strWord =~ /^($eth)($pprep)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $et_ && $strWord =~ /^($eth(?!ⲉ))($nprep)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $et_ && $strWord =~ /^($eth)(ⲛⲁ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2. "|" . $3 ;}
			elsif (++$rule_num && $strWord =~ /^($art)($eth)(ⲛⲁ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^($art)(ⲉⲧⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^($art)(ⲉⲧⲉ)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			# note for the next two rules 'n' is forbidden as a subject due to oversplitting tetn-, petn-, netn-, e.g. tetn|rOSe is not t|et|nrOSe
			elsif (++$rule_num && $strWord =~ /^($art)(ⲉⲧ(?!ⲛ)|ⲉⲧ(?:ⲉ(?=ⲧⲉⲛ)))($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^($art)(ⲉⲧ(?!ⲛ)|ⲉⲧ(?:ⲉ(?=ⲧⲉⲛ)))($ppers)($verblist)($ppero|$namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ."|". $4 . "|". $5;}
			#with nqi
			elsif (++$rule_num && $strWord =~ /^(ⲛϫⲉ|ϫⲉ)($art)($eth)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲛϫⲉ|ϫⲉ)($art)($eth)($pprep)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			elsif (++$rule_num && $strWord =~ /^(ⲛϫⲉ|ϫⲉ)($art)(ⲉⲑ)(ⲛⲁ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#with preposition
			elsif (++$rule_num && $hn_ && $strWord =~ /^($nprep)($art)($eth)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|" . $4;}
			elsif (++$rule_num && $_f && $hn_ && $strWord =~ /^($nprep)($art)($eth)($pprep)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif (++$rule_num && $hn_ && $strWord =~ /^($nprep)($art)($eth)(ⲛⲁ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|" . $4 . "|" . $5;}
			#presentative
			elsif (++$rule_num && $strWord =~ /^(ⲉⲓⲥ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲉ?ⲓⲥ)$/o) {$strWord = $1 . "|" . $2;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲉⲓⲥ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}

			#tripartite clause
			#pronominal
			elsif (++$rule_num && $tri_  && $strWord =~ /^($triprobase)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $_f && $strWord =~ /^($triprobase)($ppers)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#COMPOUND elsif (++$rule_num && $tri_  && $strWord =~ /^($triprobase)($ppers)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $tri_  && $strWord =~ /^($triprobase)($ppers)($verblist)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif (++$rule_num && $tri_  && $strWord =~ /^($triprobase)($ppers)($verblist)($possnoun)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif (++$rule_num && $tri_  && $strWord =~ /^($triprobase)($ppers)($verblist)($namelist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#2sgF
			elsif (++$rule_num && $strWord =~ /^(ⲁⲣ)($verblist)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲁⲣ)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3;}
			#COMPOUND elsif (++$rule_num && $strWord =~ /^(ⲁⲣ)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 ;}
			elsif (++$rule_num && $strWord =~ /^(ⲁⲣ)($verblist)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#proper name subject
			#elsif (++$rule_num && $tri_  && $strWord =~ /^($trinbase)($namelist)($verblist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3;}
			#elsif (++$rule_num && $_f && $tri_  && $strWord =~ /^($trinbase)($namelist)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#elsif (++$rule_num && $tri_  && $strWord =~ /^($trinbase)($namelist)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ;}
			#prenominal
			#elsif (++$rule_num && $tri_  && $strWord =~ /^($trinbase)($art|$ppos)($nounlist)($verblist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#elsif (++$rule_num && $_f && $tri_  && $strWord =~ /^($trinbase)($art|$ppos)($nounlist)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#elsif (++$rule_num && $tri_  && $strWord =~ /^($trinbase)($art|$ppos)($nounlist)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#proper name subject separate bound group
			elsif (++$rule_num && $tri_  && $strWord =~ /^($trinbase)($namelist)$/o)  {$strWord = $1 . "|" . $2;}
			#prenominal separate bound group
			elsif (++$rule_num && $tri_  && $strWord =~ /^($trinbase)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3;}

			#with je-
			#pronominal
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($triprobase)($ppers)($verblist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)($triprobase)($ppers)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#COMPOUND elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($triprobase)($ppers)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($triprobase)($ppers)($verblist)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 ."|" . $6;}
			#2sgF
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲁⲣ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲁⲣ)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#COMPOUND elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲁⲣ)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲁⲣ)($verblist)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			#proper name subject
			#elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($trinbase)($namelist)($verblist)$/)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)($trinbase)($namelist)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($trinbase)($namelist)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#prenominal
			#elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($trinbase)($art|$ppos)($nounlist)($verblist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)($trinbase)($art|$ppos)($nounlist)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6;}
			#elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($trinbase)($art|$ppos)($nounlist)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6;}
			#proper name subject separate bound group
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($trinbase)($namelist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3;}
			#prenominal separate bound group
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($trinbase)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}

			
			#Verboids
			#pronominal subject - peja=f, nanou=s
			elsif (++$rule_num && $_f && $strWord =~ /^($vbdlist)($ppero)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲛ|ⲙ(?=[ⲡⲃⲙⲫ]))($vbdlist)($ppero)$/o) {$strWord = $1 . "|" . $2  . "|" . $3;} #negated
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)($vbdlist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" .$3  ;} #with je
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ(?=[ⲡⲃⲙⲫ]))($vbdlist)($ppero)$/o) {$strWord = $1 . "|" . $2  . "|" . $3. "|" .$4;} #negated with je
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲉ|$eth|ⲛ?ⲉⲣⲉ|ⲁⲣⲉ)($vbdlist)($ppero)$/o) {$strWord = $1 . "|" . $2. "|" . $3 ;} # converted
			
			#nominal subject - peje-prwme
			#elsif (++$rule_num && $strWord =~ /^($vbdlist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $strWord =~ /^($vbdlist)($namelist)$/o) {$strWord = $1 . "|" . $2 ;}
			
			#bipartite clause
			#pronominal + future
			elsif (++$rule_num && $strWord =~ /^($bibase)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2;}
			elsif (++$rule_num && $strWord =~ /^(ⲛ|ⲙ(?=[ⲡⲃⲙⲫ]))($bibase)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2."|".$3;} #negated
			elsif (++$rule_num && $strWord =~ /^($bibase)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $_f && $strWord =~ /^($bibase)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4;}
			elsif (++$rule_num && $strWord =~ /^($bibase)(ⲛⲁ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5;}
			elsif (++$rule_num && $strWord =~ /^(ⲛ|ⲙ(?=[ⲡⲃⲙⲫ]))($bibase)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4;} #negated
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲛ|ⲙ)($bibase)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4. "|" . $5;}#negated
			elsif (++$rule_num && $strWord =~ /^(ⲛ|ⲙ(?=[ⲡⲃⲙⲫ]))($bibase)(ⲛⲁ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5. "|" . $6;}#negated
			elsif (++$rule_num && ($je_ || $et_) && $strWord =~ /^(ⲉⲧⲉ|ϫⲉ)(ⲛ|ⲙ(?=[ⲡⲃⲙⲫ]))($bibase)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2."|".$3."|".$4;} #negated converted
			#with je-
			#pronominal + future
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($bibase)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($bibase)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)($bibase)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($bibase)(ⲛⲁ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ(?=[ⲡⲃⲙⲫ]))($bibase)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ(?=[ⲡⲃⲙⲫ]))($bibase)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4. "|".$5;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ(?=[ⲡⲃⲙⲫ]))($bibase)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5. "|".$6;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ(?=[ⲡⲃⲙⲫ]))($bibase)(ⲛⲁ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6. "|".$7;}
			
			#converted bipartite clause
			#pronominal + future
			elsif (++$rule_num && $strWord =~ /^(ⲉ|$eth|ⲛ?ⲁ)($ppers)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲉ|$eth|ⲛ?ⲁ)($ppers)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲉ|$eth|ⲛ?ⲁ)($ppers)($verblist)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^(ⲉ|$eth|ⲛ?ⲁ)($ppers)($nprep)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;} #PP predicate
			elsif (++$rule_num && $strWord =~ /^(ⲉ|$eth|ⲛ?ⲁ)($ppers)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲉ|$eth|ⲛ?ⲁ)($ppers)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;}
			#nominal subject
			elsif (++$rule_num && $strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛ?ⲁⲣⲉ|ⲉⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛⲁ)($exist)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			#with je-
			#pronominal + future
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲁ|ⲉ)($ppers)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲁ|ⲉ)($ppers)($nprep)($art)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6;} #PP predicate
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲁ|ⲉ)($ppers)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲛ?ⲁ|ⲉ)($ppers)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲁⲣⲉ|ⲉⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛⲁ|ⲉ)($exist)($nounlist)$/){$strWord = $1 . "|" . $2 . "|" . $3 ."|".$4;}
			
			#double converted bipartite clause
			#pronominal + future
			elsif (++$rule_num && $strWord =~ /^(ⲉ)(ⲛⲁ)($ppers)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲉ)(ⲛⲁ)($ppers)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5 . "|" . $6;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲉ)(ⲛⲁ)($ppers)($verblist)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif (++$rule_num && $strWord =~ /^(ⲉ)(ⲛⲁ)($ppers)($nprep)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5 . "|" . $6;} #PP predicate
			elsif (++$rule_num && $strWord =~ /^(ⲉ)(ⲛⲁ)($ppers)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲉ)(ⲛⲁ)($ppers)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5 . "|" . $6;}
			#nominal subject
			elsif (++$rule_num && $strWord =~ /^(ⲉ)(ⲛⲁⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^(ⲉ)(ⲛⲁ)($exist)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}

			
			#interlocutive nominal sentence
			elsif (++$rule_num && $strWord =~ /^($pperinterloc)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2  . "|" . $3 ;}
			elsif (++$rule_num && $strWord =~ /^($pperinterloc)($namelist)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif (++$rule_num && $strWord =~ /^(ⲛ)($pperinterloc)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2  . "|" . $3. "|" . $4 ;}
			elsif (++$rule_num && $strWord =~ /^(ⲛ)($pperinterloc)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($pperinterloc)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($pperinterloc)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ)($pperinterloc)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ)($pperinterloc)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			
			
			#simple NP - moved from before "relative generic NP p-et-o, ... " to account for preterite ne|u-sotm instead of possessive *neu-sotm with nominalized verb
			#if this causes trouble consider splitting ART and PPOS cases of simple NP
			elsif (++$rule_num && $strWord =~ /^(ⲛϫⲉ|ϫⲉ|ϫⲓⲛ|ⲓⲥϫⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $strWord =~ /^($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif (++$rule_num && $strWord =~ /^([ⲡⲧⲛ]ⲁ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ;}
			elsif (++$rule_num && $strWord =~ /^(ⲛ|ⲙ(?=[ⲡⲃⲙⲫ]))($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ;}
			#elsif (++$rule_num && $strWord =~ /^(ⲛ|ⲙ(?=[ⲡⲃⲙⲫ]))([ⲡⲧⲛ]ⲁ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^(ⲛϫⲉ|ϫⲉ|ϫⲓⲛ|ⲓⲥϫⲉ)($namelist)$/o) {$strWord = $1 . "|" . $2 ;}

			#nominal separated future verb or independent/to-infinitive
			elsif(++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($verb_or_imp_list)$/o){$strWord = $1 . "|" . $2;}
			elsif(++$rule_num && $_f && $strWord =~ /^($verb_or_imp_list)($ppero|$namelist)$/o){$strWord = $1 . "|" . $2;}
			elsif(++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)($verb_or_imp_list)($ppero|$namelist)$/o){$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif(++$rule_num && $_f && $strWord =~ /^($verb_or_imp_list)($nounlist)($ppero)$/o){$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif(++$rule_num && $_f && $strWord =~ /^($verb_or_imp_list)($art|$ppos)($nounlist)$/o){$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif(++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)($verb_or_imp_list)($art|$ppos)($nounlist)$/o){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif(++$rule_num && $strWord =~ /^(ⲛⲁ|ⲉ)($verblist)$/o){$strWord = $1 . "|" . $2;}
			elsif(++$rule_num && $strWord =~ /^(ⲛⲁ|ⲉ)($verblist)($ppero|$namelist)$/o){$strWord = $1 . "|" . $2 . "|" . $3;}
			#COMPOUND elsif(++$rule_num && $strWord =~ /^(ⲛⲁ|ⲉ)($verblist)($nounlist)$/){$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif(++$rule_num && $strWord =~ /^(ⲛⲁ|ⲉ)($verblist)($art|$ppos)($nounlist)$/o){$strWord = $1 . "|" . $2 . "|" . $3."|".$4;}

			#converted tripartite clause
			#pronominal
			elsif (++$rule_num && $strWord =~ /^(ⲉ?ⲛⲧ|ⲉ|ⲛⲉ)($triprobase)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^(ⲉⲧⲉ?)(ⲁ|ⲙⲡ|ⲙⲡⲉ|ϣⲁ|ⲙⲉ|ⲙⲡⲁⲧ|ϣⲁⲛⲧⲉ?|ⲛⲛⲉ)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲉⲧⲉ?|ⲉ|ⲛⲁ)($triprobase)($ppers)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif (++$rule_num && $strWord =~ /^(ⲉⲧⲉ?|ⲉ|ⲛⲁ)($triprobase)($ppers)($verblist)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲉⲧⲉ?)(ⲙⲡ|ⲙⲡⲉ|ϣⲁ|ⲙⲉ|ⲙⲡⲁⲧ|ϣⲁⲛⲧⲉ?|ⲛⲛⲉ)($ppers)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			#COMPOUND elsif (++$rule_num && $strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)($triprobase)($ppers)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif (++$rule_num && $strWord =~ /^($art)(ⲉⲧ)(ⲁ)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;} #nominalized
			elsif (++$rule_num && $_f && $strWord =~ /^($art)(ⲉⲧ)(ⲁ)($ppers)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;} #nominalized
			elsif (++$rule_num && $strWord =~ /^($nprep)($art)(ⲉⲧ)(ⲁ)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;} 
			elsif (++$rule_num && $_f && $strWord =~ /^($nprep)($art)(ⲉⲧ)(ⲁ)($ppers)($verblist)($ppero|$namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6 . "|" . $7;}
			elsif (++$rule_num && $strWord =~ /^($art)(ⲉⲧ)(ⲁⲣ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;} #nominalized
			elsif (++$rule_num && $_f && $strWord =~ /^($art)(ⲉⲧ)(ⲁⲣ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;} #nominalized
			#prenominal
			elsif (++$rule_num && $strWord =~ /^($eth|ⲉ|ⲛⲉ)($triprobase)($art|$ppos)($nounlist)$/o)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^(ⲉⲧⲉ?)(ⲙⲡ|ⲙⲡⲉ|ϣⲁ|ⲙⲉ|ⲙⲡⲁⲧ|ϣⲁⲛⲧⲉ?|ⲛⲛⲉ)($art|$ppos)($nounlist)$/)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#elsif (++$rule_num && $strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)($verblist)$/)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#elsif (++$rule_num && $_f && $strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5. "|".$6;}
			#elsif (++$rule_num && $strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5. "|".$6;}
			elsif (++$rule_num && $strWord =~ /^($art)(ⲉⲧ)(ⲁ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}  #nominalized
			#elsif (++$rule_num && $strWord =~ /^($art)(ⲉⲛⲧ)(ⲁ)($art|$ppos)($nounlist)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5. "|" . $6;}  #nominalized
			#proper name subject separate bound group
			elsif (++$rule_num && $strWord =~ /^(ⲉⲧ|ⲉ)(ⲁ|ⲛⲛⲉ)($namelist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $strWord =~ /^(ⲉⲧⲉ?)(ⲙⲡ|ⲙⲡⲉ|ϣⲁ|ⲙⲉ|ⲙⲡⲁⲧ|ϣⲁⲛⲧⲉ?|ⲛⲧⲉⲣⲉ?|ⲛⲛⲉ)($namelist)$/o)   {$strWord = $1 . "|" . $2 . "|" . $3;}
			# relative + NP subj (ete-p-jioua pe, etere-p-rOme ...)
			elsif (++$rule_num && $strWord =~ /^($eth|ⲉⲧⲉⲣⲉ)($art|$ppos)($nounlist)$/o)   {$strWord = $1 . "|" . $2 . "|" . $3;}
			#prenominal separate bound group
			elsif (++$rule_num && $strWord =~ /^(ⲉ?ⲧ|ⲉ)(ⲁ|ⲛⲛⲉ)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			## With conjunction
			#pronominal
			elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])($eth|ⲉ)($triprobase)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ϫ[ⲉⲓ])($eth|ⲉ)($triprobase)($ppers)($verblist)($ppero)$/)  {$strWord =  $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6}
			#COMPOUND elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($ppers)($verblist)($nounlist)$/)  {$strWord =  $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;}
			elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])($art)(ⲉⲧ)(ⲁ)($ppers)($verblist)$/o) {$strWord =  $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;} #nominalized
			elsif (++$rule_num && $_f && $strWord =~ /^(ϫ[ⲉⲓ])($art)(ⲉⲧ)(ⲁ)($ppers)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6 . "|". $7;} #nominalized
			elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])($art)(ⲉⲧ)(ⲁⲣ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;} #nominalized
			elsif (++$rule_num && $_f && $strWord =~ /^(ϫ[ⲉⲓ])($art)(ⲉⲧ)(ⲁⲣ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;} #nominalized
			#prenominal
			elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])($eth|ⲉ)($triprobase)($art|$ppos)($nounlist)$/o)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)($verblist)$/)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5. "|".$6;}
			#elsif (++$rule_num && $_f && $strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)($verblist)($ppero)$/)  {$strWord =  $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6 . "|". $7;}
			#elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)($verblist)($nounlist)$/)  {$strWord =  $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6 . "|". $7;}
			elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])($art)(ⲉⲧ)(ⲁ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;}  #nominalized
			#elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])($art)(ⲉⲛⲧ)(ⲁ)($art|$ppos)($nounlist)($verblist)$/) {$strWord =  $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6 . "|". $7;}  #nominalized
			#proper name subject separate bound group
			elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])($eth|ⲉ)($triprobase)($namelist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3. "|" . $4;}
			#prenominal separate bound group
			elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])($eth|ⲉ)($triprobase)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3. "|" . $4 . "|" . $5;}
			#1sgConjunctive - if nta- didn't match converted past
			elsif (++$rule_num && $strWord =~ /^(ⲛ)(ⲧⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $strWord =~ /^(ⲛ)(ⲧⲁ)($verblist)($ppero|$namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ."|". $4;}
			elsif (++$rule_num && $strWord =~ /^(ⲛ)(ⲧⲁ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ."|". $4."|".$5;}
			#jin|nt|a|S|V|O
			elsif (++$rule_num && $strWord =~ /^(ϫⲓⲛ)(ⲉⲧ)(ⲁ)($ppers)($verblist)$/o)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			elsif (++$rule_num && $strWord =~ /^(ϫⲓⲛ)(ⲉⲧ)(ⲁ)($ppers)($verblist)($ppero)$/o)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|" . $6;}
			elsif (++$rule_num && $strWord =~ /^(ϫⲓⲛ)(ⲉⲧ)(ⲁ)($art|$ppos)($nounlist)$/o)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			elsif (++$rule_num && $strWord =~ /^(ϫⲓⲛ)(ⲉⲧ)(ⲁ)($namelist)$/o)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			
			elsif (++$rule_num && $strWord =~ /^(ⲉⲧⲉ)($namelist)$/o)  {$strWord = $1 . "|" . $2;}
			
			# prep + substitutive possessive (m-pa-p-rOme), moved to after nta- relative, for cases like nt|a|u|sOtm, nt|a|u|ti 
			elsif (++$rule_num && $hn_ && $strWord =~ /^($nprep)([ⲫⲡⲧⲑⲛ]ⲁ)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $hn_ && $strWord =~ /^($nprep|ⲛϫⲉ)([ⲫⲡⲧⲑⲛ]ⲁ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|" . $4;}
			elsif (++$rule_num && $hn_ && $strWord =~ /^([ⲫⲡⲧⲑⲛ]ⲁ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}

			
			#possessives
			elsif (++$rule_num && $strWord =~ /^((?:ⲟⲩⲟⲛⲧ|ⲙⲙⲟⲛⲧ)[ⲁⲉⲏ]?)($ppers)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $strWord =~ /^((?:ⲟⲩⲟⲛⲧ|ⲙⲙⲟⲛⲧ)[ⲁⲉⲏ]?)($ppers)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif (++$rule_num && $strWord =~ /^(ⲛⲁ|ⲉ)((?:ⲟⲩⲟⲛⲧ|ⲙⲙⲟⲛⲧ)[ⲁⲉⲏ]?)($ppers)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3."|".$4;}
			elsif (++$rule_num && $strWord =~ /^(ⲛⲁ|ⲉ)((?:ⲟⲩⲟⲛⲧ|ⲙⲙⲟⲛⲧ)[ⲁⲉⲏ]?)($ppers)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ;}

			#IMOD
			elsif (++$rule_num && $_f && $strWord =~ /^($imodlist)($ppero)$/o) {$strWord = $1 . "|" . $2;}

			#converter+prep
			elsif (++$rule_num && $strWord =~ /^($eth)($indprep)$/o) {$strWord = $1 . "|" . $2;}

			#PP with no article
			elsif (++$rule_num && $hn_ && $strWord =~ /^($nprep)($nounlist|$namelist)$/o) {$strWord = $1 . "|" . $2;}
			elsif (++$rule_num && $hn_ && $strWord =~ /^(ϫⲉ)($nprep)($nounlist|$namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ;}

			#negative or quoted imperative
			elsif (++$rule_num && $strWord =~ /^(ⲙⲡⲉⲣ|ϫⲉ)($verblist)$/o) {$strWord = $1 . "|" . $2;}
			elsif (++$rule_num && $strWord =~ /^(ⲙⲡⲉⲣ|ϫⲉ)($verblist)($ppero|$namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $strWord =~ /^(ⲙⲡⲉⲣ|ϫⲉ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^(ⲙⲡⲉⲣ|ϫⲉ)($verblist)($nounlist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲙⲡⲉⲣ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲙⲡⲉⲣ)($verblist)($ppero|$namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲙⲡⲉⲣ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|". $5;}

			#tm preposed before subject in negative conjunctive with separated verb
			elsif (++$rule_num && $strWord =~ /^(ⲛⲧⲉ)(ϣⲧⲉⲙ)($nounlist)$/o) {$strWord = $1 . "|" . $2. "|" . $3;}
			elsif (++$rule_num && $strWord =~ /^(ⲛⲧⲉ)(ϣⲧⲉⲙ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2. "|" . $3 . "|" . $4;}
			
			#p-tre-f-V style NP with or without preposition
			elsif (++$rule_num && ($hn_ || $je_) && $strWord =~ /^($nprep|ϫⲉ)(ⲡⲉ?|$ppos)(ⲑⲣⲉ)($ppero)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif (++$rule_num && ($hn_ || $je_) && $strWord =~ /^($nprep|ϫⲉ)(ⲡⲉ?|$ppos)(ⲑⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif (++$rule_num && $strWord =~ /^(ⲡⲉ?|$ppos)(ⲑⲣⲉ)($ppero)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲡⲉ?|$ppos)(ⲑⲣⲉ)($ppero)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif (++$rule_num && $strWord =~ /^(ⲡⲉ?|$ppos)(ⲑⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲡⲉ?|$ppos)(ⲑⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			
			#nominal subject incorrectly spelled together with verb + future
			# The next rule could match neinasotm as n|ei|na|sotm, with noun 'ei', if it weren't caught earlier by converted future rule
			elsif (++$rule_num && $strWord =~ /^($art|$ppos)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $_f && $strWord =~ /^($art|$ppos)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|".$5;}
			elsif (++$rule_num && $strWord =~ /^(ⲛ|ⲙ(?=[ⲡⲃⲙⲫ]))($art|$ppos)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}#negated
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲛ|ⲙ(?=[ⲡⲃⲙⲫ]))($art|$ppos)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|".$5. "|" . $6;}#negated
			elsif (++$rule_num && $strWord =~ /^($exist)($nounlist)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $strWord =~ /^($exist)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $_f && $strWord =~ /^($exist)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;}
			# with je
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ(?=[ⲡⲃⲙⲫ]))($art|$ppos)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5. "|".$6;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ(?=[ⲡⲃⲙⲫ]))($art|$ppos)($nounlist)(ⲛⲁ)($verblist)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6. "|".$7;}
			#indefinite + future
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($exist)($nounlist)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($exist)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)($exist)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6;}

			#1st person negative optative
			elsif (++$rule_num && $strWord =~ /^(ⲛⲛ)(ⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2  ."|". $3;}
			elsif (++$rule_num && $strWord =~ /^(ⲛⲛ)(ⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2  ."|". $3."|".$4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛⲛ)(ⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2  ."|". $3 ."|". $4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛⲛ)(ⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2  ."|". $3."|".$4 ."|". $5;}
			
			# morphological imperative with object
			elsif (++$rule_num && strWord =~ /^($vimplist)($art|$ppos)($nounlist)/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && strWord =~ /^($vimplist)($ppero)/o) {$strWord = $1 . "|" . $2;}

			#rarer 2sgF forms
			elsif (++$rule_num && $strWord =~ /^(ⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif (++$rule_num && $strWord =~ /^(ⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ;}
			elsif (++$rule_num && $strWord =~ /^(ⲙⲡ)(ⲉ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $strWord =~ /^(ⲙⲡ)(ⲉ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^(ⲉ)(ⲑⲣ)(ⲉ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}

			# irrealis e-ne (CCIRC + CPRET, see Layton sect. 416)
			elsif (++$rule_num && strWord =~ /^(ⲉ)(ⲛⲉ)(ⲓ|ⲕ|ϥ|ⲥ|ⲛ|ⲧⲉⲧⲛ|ⲩ)($verblist)/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && strWord =~ /^(ⲉ)(ⲛⲉ)(ⲓ|ⲕ|ϥ|ⲥ|ⲛ|ⲧⲉⲧⲛ|ⲩ)($verblist)($ppero)/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			
			# common patterns for potential auxiliary ϣ
			# negative tripartite - "wasn't/wouldn't be able to"
			elsif (++$rule_num && $strWord =~ /^(ⲛⲛⲉ|ⲙⲡⲉ?)($ppers)(ⲉ?ϣ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^(ⲛⲛⲉ|ⲙⲡⲉ?)($ppers)(ⲉ?ϣ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			# future/conditional
			elsif (++$rule_num && $strWord =~ /^($bibase)(ⲛⲁ)(ⲉ?ϣ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^($bibase)(ⲛⲁ)(ⲉ?ϣ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" .$5;}
			# future inf/relative
			elsif (++$rule_num  && $strWord =~ /^($eth)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num  && $strWord =~ /^($eth)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num  && $strWord =~ /^(ⲛⲁ)(ⲉ?ϣ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num  && $strWord =~ /^(ⲛⲁ)(ⲉ?ϣ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			# negated/converted
			elsif (++$rule_num && $strWord =~ /^(ⲛ|ϫⲉ)($bibase)(ⲛⲁ)(ⲉ?ϣ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif (++$rule_num && $strWord =~ /^(ⲛ?ⲉ)($ppers)(ⲛⲁ)(ⲉ?ϣ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif (++$rule_num && $strWord =~ /^(ⲛ|ϫⲉ)($bibase)(ⲛⲁ)(ⲉ?ϣ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;}
			elsif (++$rule_num && $strWord =~ /^(ⲛ?ⲉ)($ppers)(ⲛⲁ)(ⲉ?ϣ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;}
			
			#bipartite group incorrectly listing NP subject AND verb without space
			#nominal
			elsif (++$rule_num && $strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6;}
			#indefinite
			elsif (++$rule_num && $strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛⲉ)($exist)($nounlist)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛⲉ)($exist)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛⲉ)($exist)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5. "|".$6;}
			#converted
			#nominal
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲁⲣⲉ|ⲉⲣⲉ)($art|$ppos)($nounlist)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲁⲣⲉ|ⲉⲣⲉ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6."|".$7;}
			#indefinite
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛⲁ|ⲉ)($exist)($nounlist)($verblist|$vstatlist|$advlist)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛⲁ|ⲉ)($exist)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲛⲁ|ⲉ)($exist)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6."|".$7;}
			
			# ete|phH
			elsif (++$rule_num && $strWord =~ /^(ⲉⲧⲉ|ⲉⲣⲉ)($namelist|$ppossub)$/o) {$strWord = $1 . "|" . $2;}
			
			# ⲛⲉ+NP
			elsif (++$rule_num && $strWord =~ /^(ⲛⲉ)($namelist_pure)$/){$strWord = $1 . "|" . $2;}
			elsif (++$rule_num && $strWord =~ /^(ⲛⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;} #experimentally allowing proper nouns with articles
			
			# n|rO|k
			elsif (++$rule_num && $hn_ && $strWord =~ /^($nprep)($possnoun)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}

			# EXIST + bare noun
			elsif (++$rule_num && $strWord =~ /^(ⲟⲩⲟⲛ|ⲙⲙⲟⲛ)($nounlist)$/o) {$strWord = $1 . "|" . $2;}

			#else {			
			#nothing found
			#}

		#split off negating TMs
		if (++$rule_num && $strWord=~/(^|\|)ϣⲧⲉⲙ/ && $strWord !~ /\|ϣⲧⲉⲙ(\||ⲟ$|ⲙⲟ|ⲁⲉⲓⲏⲩ|ⲁⲓⲏⲩ|ⲁⲓⲟ|ⲁⲓⲟⲕ)(\|$ppero$)?/) {
			$strWord =~ s/^ϣⲧⲉⲙ/ϣⲧⲉⲙ|/;$strWord =~ s/\|ϣⲧⲉⲙ/|ϣⲧⲉⲙ|/;
		}
		if (++$rule_num && $strWord=~/^$ke_art\|/o) {$strWord =~ s/^([^\|]+)ⲕⲉ\|/$1\|ⲕⲉ\|/;}
		if (++$rule_num && $strWord=~/\|$ke_art\|/o) {$strWord =~ s/\|([^\|]+)ⲕⲉ\|/\|$1\|ⲕⲉ\|/;}
		
		# split irregular negation ⲙⲉϣϣⲉ
		$strWord=~ s/\|ⲙⲉϣϣⲉ/|ⲙⲉ|ϣϣⲉ/;
		
		
		$strWord =~ s/^\|//;  # No leading pipes
		$strWord =~ s/\|+/\|/; # No double pipes
		
		return($rule_num,$strWord);
}


sub begins_with
{
    return substr($_[0], 0, length($_[1])) eq $_[1];
}