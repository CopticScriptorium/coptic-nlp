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

$lexicon =  $dirname . $sep . ".." . $sep . "data" .$sep . "copt_lemma_lex.tab";
$segfile  = $dirname . $sep . ".." . $sep . "data" .$sep . "segmentation_table.tab";
$morphfile = $dirname . $sep . ".." . $sep . "data" .$sep . "morph_table.tab";


### BUILD LEXICON ###
#build function word lists
$pprep = "ⲁϫⲛⲧ|ⲉϩⲣⲁ|ⲉϫⲛⲧⲉ|ⲉϫⲱ|ⲉⲣⲁⲧ|ⲉⲣⲁⲧⲟⲩ|ⲉⲣⲟ|ⲉⲣⲱ|ⲉⲧⲃⲏⲏⲧ|ⲉⲧⲟⲟⲧ|ϩⲁⲉⲓⲁⲧ|ϩⲁϩⲧⲏ|ϩⲁⲣⲁⲧ|ϩⲁⲣⲓϩⲁⲣⲟ|ϩⲁⲣⲟ|ϩⲁⲣⲱ|ϩⲁⲧⲟⲟⲧ|ϩⲓϫⲱ|ϩⲓⲣⲱ|ϩⲓⲧⲉ|ϩⲓⲧⲟⲟⲧ|ϩⲓⲧⲟⲩⲱ|ϩⲓⲱ|ϩⲓⲱⲱ|ⲕⲁⲧⲁⲣⲟ|ⲕⲁⲧⲁⲣⲱ|ⲙⲙⲟ|ⲙⲙⲱ|ⲙⲛⲛⲥⲱ|ⲙⲡⲁⲙⲧⲟⲉⲃⲟⲗ|ⲛⲏⲧⲛ|ⲛⲁ|ⲛϩⲏⲧ|ⲛⲙⲙⲏ|ⲛⲙⲙⲁ|ⲛⲥⲁⲃⲗⲗⲁ|ⲛⲥⲱ|ⲛⲧⲟⲟⲧ|ⲟⲩⲃⲏ|ϣⲁⲣⲟ|ϣⲁⲣⲱ|ⲛⲏ|ⲛⲛⲁϩⲣⲁ|ⲟⲩⲧⲱ|ⲛⲃⲗⲁ|ⲛⲛⲁϩⲣⲏ|ϩⲁⲧⲏ|ⲉⲧⲃⲏⲏ|ⲛⲣⲁⲧ|ⲉⲣⲁ|ⲛⲁϩⲣⲁ|ⲛϩⲏ|ϩⲓⲧⲟⲟ|ⲕⲁⲧⲁ|ⲙⲉⲭⲣⲓ|ⲡⲁⲣⲁ|ⲉⲧⲃⲉ|ⲛⲧⲉ|ⲙⲛⲛⲥⲱ|ⲛⲁϩⲣⲉ?[ⲁⲙⲛ]";
$nprep = "ⲉ|ⲛ|ⲙ(?=[ⲡⲃⲙ])|ⲉⲧⲃⲉ|ϣⲁ|ⲛⲥⲁ|ⲕⲁⲧⲁ|ⲙⲛ|ϩⲓ|ⲁϫⲛ|ⲛⲧⲉ|ϩⲁⲧⲛ|ϩⲁⲧⲙ(?=[ⲡⲃⲙ])|ϩⲓⲣⲙ(?=[ⲡⲃⲙ])|ϩⲓⲣⲛ|ⲛⲃⲗ|ⲉⲣⲁⲧ|ϩⲛ|ϩⲙ(?=[ⲡⲃⲙ])|ϩⲓⲧⲛ|ϩⲓⲧⲙ(?=[ⲡⲃⲙ])|ϩⲓϫⲛ|ϩⲓϫⲙ(?=[ⲡⲃⲙ])|ϩⲁ|ⲙⲉⲭⲣⲓ|ⲡⲁⲣⲁ|ⲛⲁ|ⲛⲧⲉ|ⲛ?ⲛⲁϩⲣⲉ?[ⲙⲛ]|ⲉϫⲛ|ⲉϫⲙ(?=[ⲡⲃⲙ])";
$indprep = "ⲉⲧⲃⲉ|ϩⲛ|ϩⲙ";
$ppers = "ⲓ|ⲕ|ϥ|ⲥ|ⲛ|ⲧⲉⲧⲛ|(?<=ⲙⲡⲉ)ⲧⲛ|(?<=ϣⲁⲛⲧⲉ)ⲧⲛ|(?<=ⲧⲣⲉ)ⲧⲛ|ⲟ?ⲩ|(?<=ⲛ)ⲅ|(?<=^ⲛ)ⲥⲉ";
$ppero = "ⲓ|ⲕ|ϥ|ⲥ|ⲛ|ⲧⲛ|ⲧⲏⲩⲧⲛ|ⲟ?ⲩ|(?<=[ⲉⲟ]ⲟⲩ)ⲧ";
$pperinterloc = "ⲁⲛⲅ|ⲛⲧⲕ|ⲛⲧⲉ|ⲁⲛ|ⲁⲛⲟⲛ|ⲛⲧⲉⲧⲛ";
$indpro = 'ⲁⲛⲟⲕ$|ⲛⲧⲟⲕ$|ⲛⲧⲟ$|ⲛⲧⲟⲥ$|ⲛⲧⲟϥ$|ⲁⲛⲟⲛ$|ⲛⲧⲱⲧⲛ$|ⲛⲧⲟⲟⲩ$';
$ke_art = "(?:ⲡ|ⲧ|ⲛ|ⲡⲉⲓ|ⲧⲉⲓ|ⲛⲉⲓ|ⲟⲩ|ϩⲉⲛ)ⲕⲉ";
$femnouns = "ϩⲓⲙⲉ|ⲙⲏⲧⲉ|ϭⲟⲙ|ⲥⲁⲣⲝ|ϩⲉ|ⲉⲡⲓⲥⲧⲟⲗⲏ|ⲉⲕⲕⲗⲏⲥⲓⲁ|ⲙⲛⲧⲣⲣⲟ|ϩⲏ|ⲡⲟⲣⲛⲉⲓⲁ|ⲡⲟⲣⲛⲏ|ⲯⲩⲭⲏ|ⲙⲁⲁⲩ|ⲕⲣⲓⲥⲓⲥ|ϩⲟⲧⲉ|ⲁⲛⲁⲥⲧⲁⲥⲓⲥ|ⲡⲁⲣⲟⲩⲥⲓⲁ|ⲙⲛⲧⲣⲱⲙⲉ|ϭⲓⲛⲱⲛⲁϩ|ⲙⲛⲧⲣⲉϥⲣϩⲟⲧⲉ|ϭⲓⲛⲛⲁⲩ|ϭⲓⲛⲥⲱⲧⲙ|ϭⲓⲛϣⲱⲗⲙ|ϭⲓⲛϣⲁϫⲉ|ⲉⲛⲉⲣⲅⲓⲁ|ⲕⲟⲗⲁⲥⲓⲥ|ⲩⲛⲟⲩ|ⲧⲁⲡⲣⲟ|ⲡⲟⲗⲓⲥ|ϩⲓⲏ|ⲡⲉ|ⲕⲱⲙⲏ|ⲕⲗⲟⲟⲗⲉ|ⲅⲉⲛⲉⲁ|ⲛⲁⲩ|ⲙⲛⲧⲕⲟⲩⲓ|ⲙⲛⲧⲁⲧⲛⲁϩⲧⲉ|ϭⲓϫ|ⲛⲏⲥⲧⲓⲁ|ⲑⲁⲗⲁⲥⲥⲁ|ⲅⲉϩⲉⲛⲛⲁ|ⲥⲁⲧⲉ|ⲟⲩⲉⲣⲏⲧⲉ|ⲙⲁⲣⲧⲩⲣⲓⲁ|ⲙⲛⲧϫⲱⲱⲣⲉ|ⲟⲩⲱⲧ|ⲏⲡⲉ|ⲥⲏϥⲉ|ⲁⲫⲟⲣⲙⲏ|ⲭⲣⲉⲓⲁ|ϣⲧⲏⲛ|ϣⲉⲉⲣⲉ|ⲩϣⲏ|ⲁⲑⲏⲧ|ⲁⲧⲥⲃⲱ|ⲉⲛⲧⲟⲗⲏ|ⲃⲗⲗⲏ|ⲡⲁϣⲉ|ϩⲉⲛⲉⲉⲧⲏ|ⲥⲩⲛⲁⲅⲱⲅⲏ|ⲙⲛⲧϫⲁⲥⲓϩⲏⲧ|ⲙⲛⲧⲃⲁⲃⲉⲣⲱⲙⲉ|ⲥⲃⲱ|ⲙⲛⲧⲣⲙⲛϩⲏⲧ|ⲡⲁⲛⲟⲩⲣⲅⲓⲁ|ⲙⲛⲧϩⲁⲡⲗⲟⲩⲥ|ⲃⲁϣⲟⲣ|ⲕⲁⲕⲓⲁ|ⲛⲟⲩⲛⲉ|ⲉϩⲉ|ⲁϭⲟⲗⲧⲉ|ⲁⲥⲟⲩ|ⲧⲓⲙⲏ|ϣⲃⲉⲓⲱ|ⲙⲛⲧϩⲏⲕⲉ|ⲙⲉ|ⲙⲛⲧⲁⲑⲏⲧ|ⲟⲓⲕⲟⲩⲙⲉⲛⲏ|ⲙⲛⲧϩⲙϩⲁⲗ|ⲱⲇⲏ|ϩⲉⲗⲡⲓⲥ|ⲭⲁⲣⲓⲥ|ⲉⲓⲣⲏⲛⲏ|ⲙⲛⲧⲙⲛⲧⲣⲉ|ⲕⲟⲓⲛⲱⲛⲓⲁ|ⲥⲟⲫⲓⲁ|ⲙⲛⲧⲥⲁⲃⲉ|ⲙⲛⲧⲥⲟϭ|ⲙⲛⲧϭⲱⲃ|ⲁⲛⲁⲅⲕⲏ|ⲁⲛⲟⲙⲓⲁ|ⲡⲁⲣⲣⲏⲥⲓⲁ|ⲡⲟⲛⲏⲣⲓⲁ|ⲙⲛⲧⲁⲅⲁⲑⲟⲥ|ⲙⲛⲧⲛⲟⲩⲧⲉ|ⲙⲛⲧⲁⲧⲛⲟⲩⲧⲉ|ⲣⲓ|ⲭⲣⲓⲁ|ⲙⲛⲧⲥⲩⲛⲕⲗⲏⲧⲓⲕⲟⲥ|ⲙⲛⲧⲙⲟⲛⲁⲭⲟⲥ|ⲭⲱⲣⲁ|ⲁⲅⲉⲗⲏ|ϣⲱⲙⲉ|ⲇⲉⲕⲁⲡⲟⲗⲓⲥ|ϩⲟ|ⲡⲏⲅⲏ|ⲙⲁⲥⲧⲓⲅⲝ|ⲥϩⲓⲙⲉ|ⲡⲓⲥⲧⲓⲥ|ⲉⲝⲟⲩⲥⲓⲁ|ⲁⲡⲉ|ϩⲁⲗⲁⲥⲥⲁ|ⲡⲁⲣⲁⲇⲟⲥⲓⲥ|ⲁⲅⲟⲣⲁ|ⲡⲁⲣⲁⲃⲟⲗⲏ|ⲧⲣⲁⲡⲉⲍⲁ|ⲙⲣⲣⲉ|ⲥⲱϣⲉ|ⲇⲓⲕⲁⲓⲟⲥⲩⲛⲏ|ⲡⲁⲛϩⲟⲡⲗⲓⲁ|ⲁⲅⲁⲡⲏ|ⲙⲛⲧϩⲁⲣϣϩⲏⲧ|ϩⲩⲡⲟⲙⲟⲛⲏ|ⲙⲛⲧⲣⲙⲙⲁⲟ|ⲙⲛⲧⲡⲁⲣⲑⲉⲛⲟⲥ|ⲙⲛⲧϩⲏⲧ|ⲑⲗⲓⲯⲓⲥ";
$mascnouns = "ⲉⲓⲱⲧ|ⲥⲱⲙⲁ|ⲡⲛⲉⲩⲙⲁ|ⲣⲁⲛ|ϫⲟⲉⲓⲥ|ⲭⲣⲓⲥⲧⲟⲥ|ϩⲟⲟⲩ|ϣⲟⲩϣⲟⲩ|ⲟⲩⲱϣⲙ|ⲡⲁⲥⲭⲁ|ⲕⲟⲥⲙⲟⲥ|ⲛⲟⲩⲧⲉ|ⲡⲟⲛⲏⲣⲟⲥ|ⲃⲓⲟⲥ|ⲥⲟⲛ|ⲣⲱⲙⲉ|ⲃⲟⲗ|ⲣⲡⲉ|ⲁϩⲉ|ϣⲏⲣⲉ|ⲙⲁⲓⲣⲱⲙⲉ|ϣⲱⲛⲉ|ⲟⲩϫⲁⲓ|ⲁϣⲁⲓ|ⲛⲟϭⲛⲉϭ|ϣⲓⲡⲉ|ϩⲏⲧ|ϩⲗⲗⲟ|ϫⲡⲓⲟ|ⲙⲉⲉⲩⲉ|ⲙⲁ|ⲙⲧⲟⲛ|ⲙⲟⲧⲉ|ϭⲱⲛⲧ|ϣⲗⲏⲗ|ⲡⲓⲣⲁⲥⲙⲟⲥ|ⲡⲣⲉⲥⲃⲩⲧⲉⲣⲟⲥ|ⲁⲣⲭⲏⲉⲡⲓⲥⲕⲟⲡⲟⲥ|ϩⲟ|ϣⲁϫⲉ|ϫⲓϩⲣⲁϥ|ⲙⲏⲏϣⲉ|ⲟⲩⲉ|ⲉⲥⲏⲧ|ϫⲟⲉⲓ|ⲱⲃϣ|ⲑⲁⲃ|ⲃⲗⲗⲉ|ⲏⲓ|ⲃⲁⲡⲧⲓⲥⲧⲏⲥ|ⲟⲩⲟⲓ|ⲥⲧⲁⲩⲣⲟⲥ|ⲉⲩⲁⲅⲅⲉⲗⲓⲟⲛ|ⲉⲟⲟⲩ|ⲙⲟⲩ|ⲕⲁϩ|ⲙⲉⲣⲓⲧ|ⲧⲟⲟⲩ|ⲥⲁϩ|ⲕⲱϩⲧ|ⲙⲟⲟⲩ|ⲏⲉⲓ|ⲛⲟϭ|ⲃⲉⲕⲉ|ⲙⲁⲕϩ|ⲱⲛϩ|ⲃⲁⲗ|ϥⲛⲧ|ϩⲙⲟⲩ|ϩⲁⲅⲓⲟⲥ|ⲥⲧⲣⲁⲧⲏⲗⲁⲧⲏⲥ|ⲙⲁⲣⲧⲩⲣⲟⲥ|ϥⲁⲓⲕⲗⲟⲙ|ⲁⲅⲱⲛ|ⲉⲃⲟⲧ|ⲣⲣⲟ|ϣⲟⲣⲡ|ⲇⲓⲁⲃⲟⲗⲟⲥ|ⲙⲧⲟ|ⲥⲉⲉⲡⲉ|ⲣⲟ|ⲡⲁⲗⲗⲁϯⲟⲛ|ⲇⲓⲁⲧⲁⲅⲙⲁ|ϫⲣⲟ|ⲡⲟⲗⲉⲙⲟⲥ|ⲥⲧⲣⲁⲧⲉⲩⲙⲁ|ⲟⲣⲇⲓⲛⲟⲛ|ⲥⲧⲟⲓ|ⲗⲓⲃⲁⲛⲟⲥ|ϣⲟⲩϩⲏⲛⲉ|ϩⲟϫϩϫ|ⲛⲁⲩ|ⲁⲣⲓⲥⲧⲟⲛ|ⲧⲏⲣϥ|ⲙⲁⲕⲁⲣⲓⲟⲥ|ⲧⲃⲃⲟ|ⲅⲉⲛⲛⲁⲓⲟⲥ|ⲥⲁⲃⲃⲁⲧⲟⲛ|ⲕⲟⲙⲉⲥ|ϫⲓⲛϫⲏ|ⲡⲉⲧϩⲟⲟⲩ|ⲡⲉⲧⲛⲁⲛⲟⲩϥ|ⲃⲁⲣⲟⲥ|ϩⲟϥ|ⲡⲁⲣⲁⲇⲉⲓⲥⲟⲥ|ⲃⲟⲏⲑⲟⲥ|ⲥⲧⲉⲣⲉⲱⲙⲁ|ⲥⲟⲫⲟⲥ|ⲣⲙⲛϩⲏⲧ|ⲧⲱⲧ|ⲙⲟⲩⲓ|ⲧⲁⲉⲓⲟ|ⲥⲱϣ|ϣⲃⲣⲣϩⲱⲃ|ⲅⲣⲁⲙⲙⲁⲧⲉⲩⲥ|ϫⲱⲱⲙⲉ|ⲥⲱⲛⲧ|ⲟⲩⲟⲓⲉϣ|ⲱϩⲥ|ⲣⲏ|ⲟⲟϩ|ⲉⲙⲛⲧ|ⲓⲉⲣⲟ|ⲧⲱϩ|ⲟⲩⲱϣ|ⲙⲁⲥⲉ|ϩⲱⲃ|ⲕⲁⲓⲣⲟⲥ|ⲃⲁⲣⲃⲁⲣⲟⲥ|ⲥⲟⲃⲧⲉ|ⲣⲟⲟⲩϣ|ϩⲟⲩⲟ|ϫⲓⲛϭⲟⲛⲥ|ⲡⲁⲛⲧⲟⲕⲣⲁⲧⲱⲣ|ⲗⲁⲟⲥ|ϩⲁⲣϣϩⲏⲧ|ⲛⲁ|ⲁⲡⲟⲥⲧⲟⲗⲟⲥ|ϭⲱⲗⲡ|ⲧⲁϣⲉⲟⲉⲓϣ|ⲧⲱϩⲙ|ⲡⲛⲉⲩⲙⲁⲧⲓⲕⲟⲥ|ϩⲗⲗⲱ|ⲡⲣⲟⲫⲏⲧⲏⲥ|ϫⲁⲓⲉ|ⲟⲩⲟⲉⲓⲛ|ⲕⲁⲕⲉ|ϣⲁϩ|ϩⲏⲃⲥ|ϫⲁϫⲉ|ⲁⲅⲁⲑⲟⲥ|ⲣⲉϥⲣⲛⲟⲃⲉ|ⲁⲧⲛⲟⲩⲧⲉ|ⲛⲟⲃⲉ|ⲙⲁⲓⲛⲟⲩⲧⲉ|ⲥⲛⲟϥ|ⲙⲟⲛⲁⲭⲟⲥ|ⲕⲣⲟ|ⲟⲩⲱ|ⲁⲣⲭⲓⲥⲩⲛⲁⲅⲱⲅⲟⲥ|ϩⲁⲙϣⲉ|ϣⲟⲉⲓϣ|ϣⲧⲉⲕⲟ|ϩⲟⲩⲙⲓⲥⲉ|ⲡⲓⲛⲁⲝ|ⲟⲩⲟⲉⲓ|ⲕⲱⲧⲉ|ⲭⲟⲣⲧⲟⲥ|ⲧⲃⲧ|ⲧⲏⲩ|ⲧⲟⲡ|ⲟⲉⲓⲕ|ⲇⲁⲓⲙⲱⲛⲓⲟⲛ|ϭⲗⲟϭ|ⲗⲁⲥ|ⲥⲟⲉⲓⲧ|ⲟⲩⲟⲧⲟⲩⲉⲧ|ϩⲓⲥⲉ|ⲕⲁⲣⲡⲟⲥ|ⲕⲉ|ⲙⲓϣⲉ|ⲥⲙⲟⲧ|ⲧⲱϣ|ϩⲁⲣⲉϩ|ϫⲓⲟⲩⲉ|ϯⲧⲱⲛ|ⲕⲱϩ|ⲙⲟⲥⲧⲉ|ⲕⲣⲟϥ|ϭⲙ|ϣⲓⲛⲉ";
$mascnouns .= "|ⲉϩⲟⲟⲩ|ϩⲃⲏⲩⲉ";  # Plurals
$femnouns .= "|ⲉϩⲟⲟⲩ|ϩⲃⲏⲩⲉ";  # Plurals
$nofemnouns = "(?!(?:" . $femnouns .")\$)";
$nomascnouns = "(?!(?:" . $mascnouns .")\$)";

$art = "ⲡ" . $nofemnouns . "|ⲡⲉ(?=(?:[^ⲁⲉⲓⲟⲩⲏⲱ][^ⲁⲉⲓⲟⲩⲏⲱ]|ⲯ|ⲭ|ⲑ|ⲫ|ⲝ|ϩⲟⲟⲩ|ⲟ?ⲩⲟⲉⲓϣ|ⲣⲟⲙⲡⲉ|ⲟ?ⲩϣⲏ|ⲟ?ⲩⲛⲟⲩ))|ⲛ|ⲛⲉ(?=(?:[^ⲁⲉⲓⲟⲩⲏⲱ][^ⲁⲉⲓⲟⲩⲏⲱ]|ⲯ|ⲭ|ⲑ|ⲫ|ⲝ|ϩⲟⲟⲩ|ⲟ?ⲩⲟⲉⲓϣ|ⲣⲟⲙⲡⲉ|ⲟ?ⲩϣⲏ|ⲟ?ⲩⲛⲟⲩ))|ⲧ".$nomascnouns."|ⲧⲉ(?=(?:[^ⲁⲉⲓⲟⲩⲏⲱ][^ⲁⲉⲓⲟⲩⲏⲱ]|ⲯ|ⲭ|ⲑ|ⲫ|ⲝ|ϩⲟⲟⲩ|ⲟ?ⲩⲟⲉⲓϣ|ⲣⲟⲙⲡⲉ|ⲟ?ⲩϣⲏ|ⲟ?ⲩⲛⲟⲩ))|ⲟⲩ|(?<=[ⲁⲉ])ⲩ|ϩⲉⲛ|ⲡⲉⲓ|ⲧⲉⲓ|ⲛⲉⲓ|ⲕⲉ|ⲙ(?=[ⲙⲡⲃ])|ⲡⲓ|ⲛⲓ|ϯ";
$art = $art . "|" . $ke_art;
$ppos = "[ⲡⲧⲛ]ⲉ[ⲕϥⲥⲛⲩ]|[ⲡⲧⲛ]ⲉⲧⲛ|[ⲡⲧⲛ]ⲁ|[ⲡⲧⲛ]ⲟⲩ";
$triprobase = "ⲁ|ⲙⲡ|ⲙⲡⲉ|ϣⲁ|ⲙⲉ|ⲙⲡⲁⲧ|ϣⲁⲛⲧⲉ?|ⲛⲧⲉⲣⲉ?|ⲛⲛⲉ|ⲛⲧⲉ|ⲛ(?=(?:ⲧⲁ|ⲅ|ϥ|ⲧⲛ|ⲧⲉⲧⲛ|ⲥⲉ))|ⲧⲣⲉ|ⲧⲁⲣⲉ|ⲙⲁⲣⲉ|ⲙⲡⲣⲧⲣⲉ"; 
$trinbase = "ⲁ|ⲙⲡⲉ|ϣⲁⲣⲉ|ⲙⲉⲣⲉ|ⲙⲡⲁⲧⲉ|ϣⲁⲛⲧⲉ|ⲛⲧⲉⲣⲉ|ⲛⲛⲉ|ⲛⲧⲉⲣⲉ|ⲛⲧⲉ|ⲧⲣⲉ|ⲧⲁⲣⲉ|ⲙⲁⲣⲉ|ⲙⲡⲣⲧⲣⲉ|ⲉⲣϣⲁⲛ";
$bibase = "ϯ|ⲧⲉ|ⲕ|ϥ|ⲥ|ⲧⲛ|ⲧⲉⲧⲛ|ⲥⲉ";
$exist = "ⲟⲩⲛ|ⲙ?ⲙⲛ";

#get external open class lexicon
if ($lexicon ne "")
{
open LEX,"<:encoding(UTF-8)",$lexicon or die "could not find lexicon file $lexicon";
while (<LEX>) {
    chomp;
	if ($_ =~ /^(.*)\t(.*)\t(.*)$/) #ignore comments in modifier file marked by #
    {
	if ($2 eq 'N') {$nounlist .= "$1|";} 
	if ($2 eq 'NPROP') {$namelist .= "$1|";} 
	elsif ($2 eq 'V' || $2 eq 'VIMP') {
			if ($1 eq 'ⲛ'){  # special handlers for unusual/overgenerating verbs
				$verblist .= "$1(?=[^\s])|";
			}
			elsif ($1 eq 'ⲉⲣ'){
				$verblist .= "(?<!ⲥ)$1|";
			}
			else{
				$verblist .= "$1|";
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
$tm =~ s/\|/|ⲧⲙ/g;
$verblist .=  "$tm";
$verblist .=  "|ⲙⲉϣϣⲉ";

#add noun derivations
$at = $verblist;
$at =~ s/\|/|(?:(?:ⲙⲛⲧ)?ⲁⲧ|ⲣⲉϥ|ⲙⲛⲧ)/g;
$nounlist .=  "$at";

$nounlist .="ⲥⲁⲧⲁⲛⲁⲥ|%%%";
$verblist .="%%%";
$vstatlist .="%%%";
$advlist .="%%%";
$namelist_pure = $namelist;
$namelist .= $indpro;
$namelist .="|ⲡⲁⲓ|ⲧⲁⲓ|ⲛⲁⲓ|ϭⲉ|ϩⲓⲟⲛⲉ|ⲛⲓⲙ|ⲟⲩ|ⲗⲁⲁⲩ|%%%";
$namelist_pure .= "|ⲡⲁⲓ|ⲧⲁⲓ|ⲛⲁⲓ|ϭⲉ|ϩⲓⲟⲛⲉ|ⲛⲓⲙ|ⲟⲩ|ⲗⲁⲁⲩ|%%%";
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
			if(++$rule_num && $strWord =~ /^($nprep|$pprep)?(ⲑ|ⲫ)(.+)$/o)
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
			
			if(++$rule_num && $strWord =~ /^((?:(?:$nprep|$pprep)?$art)?ⲉⲑ)(.+)$/o)
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
			$et_ = &begins_with($strWord, "ⲉⲧ");
			$je_ = &begins_with($strWord, "ϫⲉ");
			$mns_ = &begins_with($strWord, "ⲙⲛⲛⲥⲁ");
			$ant_ = &begins_with($strWord, "ⲁⲛⲧⲓ");
			$hn_ = $strWord =~ m/^$nprep/o;
			$_f = $strWord =~ m/$ppero$/o;
			$tri_ = ($strWord =~ m/$triprobase/o || &begins_with($strWord, "ⲉⲣϣⲁⲛ"));
			
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
			elsif (++$rule_num && $strWord =~ /^(ⲉ)($ppers)(ⲉ|ϣⲁⲛ)($verblist)$/o) {$strWord = $1 . $2 . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^(ⲉ)($ppers)(ⲉ|ϣⲁⲛ)($verblist)($ppero|$namelist)$/o) {$strWord = $1 . $2 . $3 . "|" . $4."|" . $5;}  #COMPOUND: $nounlist
			elsif (++$rule_num && $strWord =~ /^(ⲉ)($ppers)(ⲉ|ϣⲁⲛ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . $2 . $3 . "|" . $4."|" . $5."|" . $6;}
			
			
			#ⲧⲏⲣ=
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲧⲏⲣ)($ppero)$/){$strWord = $1 ."|" . $2;}

			#pure existential
			elsif (++$rule_num && $strWord =~ /^(ⲟⲩⲛ|ⲙⲛ)($nounlist)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif (++$rule_num && $strWord =~ /^(ϫⲉ)(ⲟⲩⲛ|ⲙⲛ)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}

			#tre- causative infinitives
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲣⲉ)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $_f && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲣⲉ)($ppers)($verblist)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲣ)(ⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $_f && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲣ)(ⲁ)($verblist)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲣⲉ)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲙ)(ⲧⲣⲉ)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $_f && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲙ)(ⲧⲣⲉ)($ppers)($verblist)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲙ)(ⲧⲣ)(ⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $_f && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲙ)(ⲧⲣ)(ⲁ)($verblist)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲙ)(ⲧⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif(++$rule_num && ($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲙ)(ⲧⲣⲉ)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}

			#prepositions
			elsif (++$rule_num && $_f && $strWord =~ /^($pprep)($ppero)$/){$strWord = $1 . "|" . $2;}
			elsif (++$rule_num && $hn_ && $strWord =~ /^($nprep)($namelist_pure)$/){$strWord = $1 . "|" . $2;}
			elsif (++$rule_num && $hn_ && $strWord =~ /^($nprep)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;} #experimentally allowing proper nouns with articles
			elsif (++$rule_num && $hn_ && $strWord =~ /^($nprep)([ⲡⲧⲛ]ⲁ)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $hn_ && $strWord =~ /^($nprep)([ⲡⲧⲛ]ⲁ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|" . $4;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)($pprep)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($nprep)($namelist)$/){$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($nprep)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;} #experimentally allowing proper nouns with articles
			#elsif ($strWord =~ /^($nprep)($art|$ppos)ⲉ($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}

			#elsif ($strWord =~ /^($art|$ppos)($namelist)$/o) {$strWord = $1 . "|" . $2 ;} #experimental, allow names with article
			#relative generic NP p-et-o, ... 
			elsif (++$rule_num && $et_ && $strWord =~ /^(ⲉⲧ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif (++$rule_num && $strWord =~ /^($art)(ⲉⲧ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $_f && $strWord =~ /^($art)(ⲉⲧ)($pprep)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $et_ && $strWord =~ /^(ⲉⲧ)(ⲛⲁ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2. "|" . $3 ;}
			elsif (++$rule_num && $strWord =~ /^($art)(ⲉⲧ)(ⲛⲁ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^($art)(ⲉⲧⲉⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^($art)(ⲉⲧⲉⲣⲉ)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			#with nqi
			elsif (++$rule_num && $strWord =~ /^(ⲛϭⲓ|ϫⲉ)($art)(ⲉⲧ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲛϭⲓ|ϫⲉ)($art)(ⲉⲧ)($pprep)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			elsif (++$rule_num && $strWord =~ /^(ⲛϭⲓ|ϫⲉ)($art)(ⲉⲧ)(ⲛⲁ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#with preposition
			elsif (++$rule_num && $hn_ && $strWord =~ /^($nprep)($art)(ⲉⲧ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|" . $4;}
			elsif (++$rule_num && $_f && $hn_ && $strWord =~ /^($nprep)($art)(ⲉⲧ)($pprep)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif (++$rule_num && $hn_ && $strWord =~ /^($nprep)($art)(ⲉⲧ)(ⲛⲁ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|" . $4 . "|" . $5;}
			#presentative
			elsif (++$rule_num && $strWord =~ /^(ⲉⲓⲥ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲉⲓⲥ)$/o) {$strWord = $1 . "|" . $2;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲉⲓⲥ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}

			#tripartite clause
			#pronominal
			elsif (++$rule_num && $tri_  && $strWord =~ /^($triprobase)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $_f && $strWord =~ /^($triprobase)($ppers)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#COMPOUND elsif (++$rule_num && $tri_  && $strWord =~ /^($triprobase)($ppers)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $tri_  && $strWord =~ /^($triprobase)($ppers)($verblist)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
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
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲛ|ⲙ)($vbdlist)($ppero)$/o) {$strWord = $1 . "|" . $2  . "|" . $3;} #negated
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)($vbdlist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" .$3  ;} #with je
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ)($vbdlist)($ppero)$/o) {$strWord = $1 . "|" . $2  . "|" . $3. "|" .$4;} #negated with je
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲉⲧ?|ⲛ?ⲉⲣⲉ)($vbdlist)($ppero)$/o) {$strWord = $1 . "|" . $2. "|" . $3 ;} # converted
			
			#nominal subject - peje-prwme
			#elsif (++$rule_num && $strWord =~ /^($vbdlist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $strWord =~ /^($vbdlist)($namelist)$/o) {$strWord = $1 . "|" . $2 ;}
			
			#bipartite clause
			#pronominal + future
			elsif (++$rule_num && $strWord =~ /^($bibase)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2;}
			elsif (++$rule_num && $strWord =~ /^(ⲛ|ⲙ)($bibase)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2."|".$3;} #negated
			elsif (++$rule_num && $strWord =~ /^($bibase)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $_f && $strWord =~ /^($bibase)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4;}
			elsif (++$rule_num && $strWord =~ /^($bibase)(ⲛⲁ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5;}
			elsif (++$rule_num && $strWord =~ /^($art|$ppos)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $_f && $strWord =~ /^($art|$ppos)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|".$5;}
			elsif (++$rule_num && $strWord =~ /^(ⲛ|ⲙ)($bibase)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4;} #negated
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲛ|ⲙ)($bibase)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4. "|" . $5;}#negated
			elsif (++$rule_num && $strWord =~ /^(ⲛ|ⲙ)($bibase)(ⲛⲁ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5. "|" . $6;}#negated
			elsif (++$rule_num && $strWord =~ /^(ⲛ|ⲙ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}#negated
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲛ|ⲙ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|".$5. "|" . $6;}#negated
			#indefinite + future
			elsif (++$rule_num && $strWord =~ /^($exist)($nounlist)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $strWord =~ /^($exist)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $_f && $strWord =~ /^($exist)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;}
			#with je-
			#pronominal + future
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($bibase)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($bibase)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)($bibase)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($bibase)(ⲛⲁ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ)($bibase)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ)($bibase)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4. "|".$5;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ)($bibase)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5. "|".$6;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ)($bibase)(ⲛⲁ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6. "|".$7;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5. "|".$6;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6. "|".$7;}
			#indefinite + future
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($exist)($nounlist)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)($exist)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)($exist)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6;}
			
			#converted bipartite clause
			#pronominal + future
			elsif (++$rule_num && $strWord =~ /^(ⲉⲧ?|ⲛⲉ)($ppers)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲉⲧ?|ⲛⲉ)($ppers)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;}
			elsif (++$rule_num && $strWord =~ /^(ⲉⲧ?|ⲛⲉ)($ppers)($nprep)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;} #PP predicate
			elsif (++$rule_num && $strWord =~ /^(ⲉⲧ?|ⲛⲉ)($ppers)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲉⲧ?|ⲛⲉ)($ppers)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;}
			#nominal
			elsif (++$rule_num && $strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6;}
			elsif (++$rule_num && $strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			#indefinite
			elsif (++$rule_num && $strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛⲉ)($exist)($nounlist)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛⲉ)($exist)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛⲉ)($exist)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5. "|".$6;}
			elsif (++$rule_num && $strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛⲉ)($exist)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			#with je-
			#pronominal + future
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉ)($ppers)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉ)($ppers)($nprep)($art)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6;} #PP predicate
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉ)($ppers)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉ)($ppers)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6;}
			#nominal
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6."|".$7;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#indefinite
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉ)($exist)($nounlist)($verblist|$vstatlist|$advlist)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉ)($exist)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6;}
			elsif (++$rule_num && $je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉ)($exist)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6."|".$7;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉ)($exist)($nounlist)$/){$strWord = $1 . "|" . $2 . "|" . $3 ."|".$4;}
			
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
			elsif (++$rule_num && $strWord =~ /^(ⲛϭⲓ|ϫⲉ|ϫⲓⲛ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $strWord =~ /^($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif (++$rule_num && $strWord =~ /^([ⲡⲧⲛ]ⲁ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ;}
			elsif (++$rule_num && $strWord =~ /^(ⲛ|ⲙ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ;}
			elsif (++$rule_num && $strWord =~ /^(ⲛ|ⲙ)([ⲡⲧⲛ]ⲁ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^(ⲛϭⲓ|ϫⲉ|ϫⲓⲛ)($namelist)$/o) {$strWord = $1 . "|" . $2 ;}

			#nominal separated future verb or independent/to-infinitive
			elsif(++$rule_num && $_f && $strWord =~ /^($verblist)($ppero)$/){$strWord = $1 . "|" . $2;}
			elsif(++$rule_num && $strWord =~ /^(ⲛⲁ|ⲉ)($verblist)$/){$strWord = $1 . "|" . $2;}
			elsif(++$rule_num && $strWord =~ /^(ⲛⲁ|ⲉ)($verblist)($ppero|$namelist)$/){$strWord = $1 . "|" . $2 . "|" . $3;}
			#COMPOUND elsif(++$rule_num && $strWord =~ /^(ⲛⲁ|ⲉ)($verblist)($nounlist)$/){$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif(++$rule_num && $strWord =~ /^(ⲛⲁ|ⲉ)($verblist)($art|$ppos)($nounlist)$/){$strWord = $1 . "|" . $2 . "|" . $3."|".$4;}

			#converted tripartite clause
			#pronominal
			elsif (++$rule_num && $strWord =~ /^(ⲉ?ⲛⲧ|ⲉ|ⲛⲉ)($triprobase)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ⲉ?ⲛⲧ|ⲉ|ⲛⲉ)($triprobase)($ppers)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			#COMPOUND elsif (++$rule_num && $strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)($triprobase)($ppers)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif (++$rule_num && $strWord =~ /^($art)(ⲉⲛⲧ)(ⲁ)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;} #nominalized
			elsif (++$rule_num && $_f && $strWord =~ /^($art)(ⲉⲛⲧ)(ⲁ)($ppers)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;} #nominalized
			elsif (++$rule_num && $strWord =~ /^($art)(ⲉⲛⲧ)(ⲁⲣ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;} #nominalized
			elsif (++$rule_num && $_f && $strWord =~ /^($art)(ⲉⲛⲧ)(ⲁⲣ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;} #nominalized
			#prenominal
			elsif (++$rule_num && $strWord =~ /^(ⲉ?ⲛⲧ|ⲉ|ⲛⲉ)($triprobase)($art|$ppos)($nounlist)$/)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#elsif (++$rule_num && $strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)($verblist)$/)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#elsif (++$rule_num && $_f && $strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5. "|".$6;}
			#elsif (++$rule_num && $strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5. "|".$6;}
			elsif (++$rule_num && $strWord =~ /^($art)(ⲉⲛⲧ)(ⲁ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}  #nominalized
			#elsif (++$rule_num && $strWord =~ /^($art)(ⲉⲛⲧ)(ⲁ)($art|$ppos)($nounlist)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5. "|" . $6;}  #nominalized
			#proper name subject separate bound group
			elsif (++$rule_num && $strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)(ⲁ|ⲛⲛⲉ)($namelist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3;}
			#prenominal separate bound group
			elsif (++$rule_num && $strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)(ⲁ|ⲛⲛⲉ)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			## With conjunction
			#pronominal
			elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif (++$rule_num && $_f && $strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($ppers)($verblist)($ppero)$/)  {$strWord =  $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6}
			#COMPOUND elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($ppers)($verblist)($nounlist)$/)  {$strWord =  $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;}
			elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])($art)(ⲉⲛⲧ)(ⲁ)($ppers)($verblist)$/) {$strWord =  $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;} #nominalized
			elsif (++$rule_num && $_f && $strWord =~ /^(ϫ[ⲉⲓ])($art)(ⲉⲛⲧ)(ⲁ)($ppers)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6 . "|". $7;} #nominalized
			elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])($art)(ⲉⲛⲧ)(ⲁⲣ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;} #nominalized
			elsif (++$rule_num && $_f && $strWord =~ /^(ϫ[ⲉⲓ])($art)(ⲉⲛⲧ)(ⲁⲣ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;} #nominalized
			#prenominal
			elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)$/o)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)($verblist)$/)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5. "|".$6;}
			#elsif (++$rule_num && $_f && $strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)($verblist)($ppero)$/)  {$strWord =  $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6 . "|". $7;}
			#elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)($verblist)($nounlist)$/)  {$strWord =  $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6 . "|". $7;}
			elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])($art)(ⲉⲛⲧ)(ⲁ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;}  #nominalized
			#elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])($art)(ⲉⲛⲧ)(ⲁ)($art|$ppos)($nounlist)($verblist)$/) {$strWord =  $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6 . "|". $7;}  #nominalized
			#proper name subject separate bound group
			elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($namelist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3. "|" . $4;}
			#prenominal separate bound group
			elsif (++$rule_num && $strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3. "|" . $4 . "|" . $5;}
			#1sgConjunctive - if nta- didn't match converted past
			elsif (++$rule_num && $strWord =~ /^(ⲛ)(ⲧⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $strWord =~ /^(ⲛ)(ⲧⲁ)($verblist)($ppero|$namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ."|". $4;}
			elsif (++$rule_num && $strWord =~ /^(ⲛ)(ⲧⲁ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ."|". $4."|".$5;}
			#jin|nt|a|S|V|O
			elsif (++$rule_num && $strWord =~ /^(ϫⲓⲛ)(ⲛⲧ)(ⲁ)($ppers)($verblist)$/o)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			elsif (++$rule_num && $strWord =~ /^(ϫⲓⲛ)(ⲛⲧ)(ⲁ)($ppers)($verblist)($ppero)$/o)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|" . $6;}
			elsif (++$rule_num && $strWord =~ /^(ϫⲓⲛ)(ⲛⲧ)(ⲁ)($art|$ppos)($nounlist)$/o)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			elsif (++$rule_num && $strWord =~ /^(ϫⲓⲛ)(ⲛⲧ)(ⲁ)($namelist)$/o)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			
			
			#possessives
			elsif (++$rule_num && $strWord =~ /^((?:ⲟⲩⲛⲧ|ⲙⲛⲧ)[ⲁⲉⲏ]?)($ppers)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $strWord =~ /^((?:ⲟⲩⲛⲧ|ⲙⲛⲧ)[ⲁⲉⲏ]?)($ppers)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif (++$rule_num && $strWord =~ /^(ⲛⲉ|ⲉ)((?:ⲟⲩⲛⲧ|ⲙⲛⲧ)[ⲁⲉⲏ]?)($ppers)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3."|".$4;}
			elsif (++$rule_num && $strWord =~ /^(ⲛⲉ|ⲉ)((?:ⲟⲩⲛⲧ|ⲙⲛⲧ)[ⲁⲉⲏ]?)($ppers)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ;}

			#IMOD
			elsif (++$rule_num && $_f && $strWord =~ /^($imodlist)($ppero)$/o) {$strWord = $1 . "|" . $2;}

			#converter+prep
			elsif (++$rule_num && $strWord =~ /^(ⲉⲧ)($indprep)$/o) {$strWord = $1 . "|" . $2;}

			#PP with no article
			elsif (++$rule_num && $hn_ && $strWord =~ /^($nprep)($nounlist|$namelist)$/o) {$strWord = $1 . "|" . $2;}
			elsif (++$rule_num && $hn_ && $strWord =~ /^(ϫⲉ)($nprep)($nounlist|$namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ;}

			#negative or quoted imperative
			elsif (++$rule_num && $strWord =~ /^(ⲙⲡⲣ|ϫⲉ)($verblist)$/o) {$strWord = $1 . "|" . $2;}
			elsif (++$rule_num && $strWord =~ /^(ⲙⲡⲣ|ϫⲉ)($verblist)($ppero|$namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $strWord =~ /^(ⲙⲡⲣ|ϫⲉ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $strWord =~ /^(ⲙⲡⲣ|ϫⲉ)($verblist)($nounlist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲙⲡⲣ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲙⲡⲣ)($verblist)($ppero|$namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲙⲡⲣ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|". $5;}

			#tm preposed before subject in negative conjunctive with separated verb
			elsif (++$rule_num && $strWord =~ /^(ⲛⲧⲉ)(ⲧⲙ)($nounlist)$/o) {$strWord = $1 . "|" . $2. "|" . $3;}
			
			#p-tre-f-V style NP with or without preposition
			elsif (++$rule_num && ($hn_ || $je_) && $strWord =~ /^($nprep|ϫⲉ)(ⲡⲉ?|$ppos)(ⲧⲣⲉ)($ppero)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif (++$rule_num && ($hn_ || $je_) && $strWord =~ /^($nprep|ϫⲉ)(ⲡⲉ?|$ppos)(ⲧⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif (++$rule_num && $strWord =~ /^(ⲡⲉ?|$ppos)(ⲧⲣⲉ)($ppero)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲡⲉ?|$ppos)(ⲧⲣⲉ)($ppero)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif (++$rule_num && $strWord =~ /^(ⲡⲉ?|$ppos)(ⲧⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif (++$rule_num && $je_ && $strWord =~ /^(ϫⲉ)(ⲡⲉ?|$ppos)(ⲧⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			
			#else {			
			#nothing found
			#}	

		#split off negating TMs
		if (++$rule_num && $strWord=~/\|ⲧⲙ(?!ⲁⲉⲓⲏⲩ|ⲁⲓⲏⲩ|ⲁⲓⲟ|ⲁⲓⲟⲕ|ⲙⲟ|ⲟ$|\|)/) {$strWord =~ s/\|ⲧⲙ/|ⲧⲙ|/;}
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