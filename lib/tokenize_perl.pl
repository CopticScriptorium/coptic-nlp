use Getopt::Std;
use utf8;
binmode(STDOUT, ":utf8");
binmode(STDIN, ":utf8");

use File::Basename;
my $dirname = dirname(__FILE__);

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
$art = "ⲡ|ⲡⲉ(?=(?:[^ⲁⲉⲓⲟⲩⲏⲱ][^ⲁⲉⲓⲟⲩⲏⲱ]|ⲯ|ⲭ|ⲑ|ⲫ|ⲝ|ϩⲟⲟⲩ|ⲟ?ⲩⲟⲉⲓϣ|ⲣⲟⲙⲡⲉ|ⲟ?ⲩϣⲏ|ⲟ?ⲩⲛⲟⲩ))|ⲛ|ⲛⲉ(?=(?:[^ⲁⲉⲓⲟⲩⲏⲱ][^ⲁⲉⲓⲟⲩⲏⲱ]|ⲯ|ⲭ|ⲑ|ⲫ|ⲝ|ϩⲟⲟⲩ|ⲟ?ⲩⲟⲉⲓϣ|ⲣⲟⲙⲡⲉ|ⲟ?ⲩϣⲏ|ⲟ?ⲩⲛⲟⲩ))|ⲧ|ⲧⲉ(?=(?:[^ⲁⲉⲓⲟⲩⲏⲱ][^ⲁⲉⲓⲟⲩⲏⲱ]|ⲯ|ⲭ|ⲑ|ⲫ|ⲝ|ϩⲟⲟⲩ|ⲟ?ⲩⲟⲉⲓϣ|ⲣⲟⲙⲡⲉ|ⲟ?ⲩϣⲏ|ⲟ?ⲩⲛⲟⲩ))|ⲟⲩ|(?<=[ⲁⲉ])ⲩ|ϩⲉⲛ|ⲡⲉⲓ|ⲧⲉⲓ|ⲛⲉⲓ|ⲕⲉ|ⲙ(?=[ⲙⲡⲃ])|ⲡⲓ|ⲛⲓ|ϯ";
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
	elsif ($2 eq 'V' || $2 eq 'VIMP') {	$verblist .= "$1|";} 
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
	$res = &tokenize($line);
	print $res . "\n";
}


sub tokenize{
	$strWord = $_[0];
		
			#Activate?
			#if ($strWord =~ m/ⲑ\|/ && $trust_tokenization == 1) {
			#	$strWord =~ s/\|//g;
			#}

			#check for theta/phi containing an article
			if($strWord =~ /^($nprep|$pprep)?(ⲑ|ⲫ)(.+)$/o) 
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
			
			if($strWord =~ /^((?:(?:$nprep|$pprep)?$art)?ⲉⲑ)(.+)$/o) 
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
			if($strWord =~ /^(ϣⲁⲛ|ⲙⲡⲁ)ϯ(.*)/) 
			{
				$candidate = $1;
				$candidate .=  "ⲧ";
				if (defined($2)){$ending = $2;}else{$ending="";}
				if ($candidate =~ /^($triprobase|$pprep)$/o) 
				{
					$strWord = $candidate . "ⲓ". $ending;
				}
			}
			elsif($strWord =~ /^(.*)ϯ(.+)$/) 
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
			if ($strWord eq "ⲛⲁⲩ"){$strWord = "ⲛⲁ|ⲩ";} #free standing nau is a PP not a V
			elsif ($strWord eq "ⲛⲁϣ"){$strWord = "ⲛ|ⲁϣ";} #"in which (way)"
			elsif ($strWord eq "ⲉⲓⲣⲉ"){$strWord = "ⲉⲓⲣⲉ";} #free standing eire is not e|i|re
			elsif ($strWord eq "ϩⲟⲡⲟⲩ"){$strWord = "ϩⲟⲡⲟⲩ";} #free standing hopou is not hop|ou
			elsif ($strWord eq "ⲉϫⲓ"){$strWord = "ⲉ|ϫⲓ";} 
			elsif ($strWord eq "ⲛⲏⲧⲛ"){$strWord = "ⲛⲏ|ⲧⲛ";} 

			#check stoplist
			elsif (exists $stoplist{$strWord}) {$strWord = $strWord;} 

			#check segmentation file
			elsif (exists $segs{$strWord}) {$strWord = $segs{$strWord};} 
			
			#adverbs
			elsif ($strWord =~ /^($advlist)$/){$strWord = $1;}
			
			#optative/conditional, make ppers a portmanteau segment with base
			elsif ($strWord =~ /^(ⲉ)($ppers)(ⲉ|ϣⲁⲛ)($verblist)$/o) {$strWord = $1 . $2 . $3 . "|" . $4;}
			elsif ($strWord =~ /^(ⲉ)($ppers)(ⲉ|ϣⲁⲛ)($verblist)($ppero|$namelist)$/o) {$strWord = $1 . $2 . $3 . "|" . $4."|" . $5;}  #COMPOUND: $nounlist 
			elsif ($strWord =~ /^(ⲉ)($ppers)(ⲉ|ϣⲁⲛ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . $2 . $3 . "|" . $4."|" . $5."|" . $6;}
			
			
			#ⲧⲏⲣ=
			elsif ($_f && $strWord =~ /^(ⲧⲏⲣ)($ppero)$/){$strWord = $1 ."|" . $2;}

			#pure existential
			elsif ($strWord =~ /^(ⲟⲩⲛ|ⲙⲛ)($nounlist)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif ($strWord =~ /^(ϫⲉ)(ⲟⲩⲛ|ⲙⲛ)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}

			#tre- causative infinitives
			elsif(($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲣⲉ)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif(($et_ || $mns_ || $ant_) && $_f && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲣⲉ)($ppers)($verblist)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif(($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲣ)(ⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif(($et_ || $mns_ || $ant_) && $_f && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲣ)(ⲁ)($verblist)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif(($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif(($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲣⲉ)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif(($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲙ)(ⲧⲣⲉ)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif(($et_ || $mns_ || $ant_) && $_f && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲙ)(ⲧⲣⲉ)($ppers)($verblist)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;}
			elsif(($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲙ)(ⲧⲣ)(ⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif(($et_ || $mns_ || $ant_) && $_f && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲙ)(ⲧⲣ)(ⲁ)($verblist)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;}
			elsif(($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲙ)(ⲧⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif(($et_ || $mns_ || $ant_) && $strWord =~ /^(ⲉ|ⲙⲛⲛⲥⲁ|ⲁⲛⲧⲓ)(ⲧⲙ)(ⲧⲣⲉ)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}

			#prepositions
			elsif ($_f && $strWord =~ /^($pprep)($ppero)$/){$strWord = $1 . "|" . $2;}
			elsif ($hn_ && $strWord =~ /^($nprep)($namelist_pure)$/){$strWord = $1 . "|" . $2;}
			elsif ($hn_ && $strWord =~ /^($nprep)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;} #experimentally allowing proper nouns with articles
			elsif ($hn_ && $strWord =~ /^($nprep)([ⲡⲧⲛ]ⲁ)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;} 
			elsif ($hn_ && $strWord =~ /^($nprep)([ⲡⲧⲛ]ⲁ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|" . $4;} 
			elsif ($je_ && $_f && $strWord =~ /^(ϫⲉ)($pprep)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)($nprep)($namelist)$/){$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)($nprep)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;} #experimentally allowing proper nouns with articles
			#elsif ($strWord =~ /^($nprep)($art|$ppos)ⲉ($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}

			#elsif ($strWord =~ /^($art|$ppos)($namelist)$/o) {$strWord = $1 . "|" . $2 ;} #experimental, allow names with article
			#relative generic NP p-et-o, ... 
			elsif ($et_ && $strWord =~ /^(ⲉⲧ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif ($strWord =~ /^($art)(ⲉⲧ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif ($_f && $strWord =~ /^($art)(ⲉⲧ)($pprep)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($et_ && $strWord =~ /^(ⲉⲧ)(ⲛⲁ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2. "|" . $3 ;}
			elsif ($strWord =~ /^($art)(ⲉⲧ)(ⲛⲁ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|" . $4;}
			elsif ($strWord =~ /^($art)(ⲉⲧⲉⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($strWord =~ /^($art)(ⲉⲧⲉⲣⲉ)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			#with nqi
			elsif ($strWord =~ /^(ⲛϭⲓ|ϫⲉ)($art)(ⲉⲧ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($_f && $strWord =~ /^(ⲛϭⲓ|ϫⲉ)($art)(ⲉⲧ)($pprep)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			elsif ($strWord =~ /^(ⲛϭⲓ|ϫⲉ)($art)(ⲉⲧ)(ⲛⲁ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#with preposition
			elsif ($hn_ && $strWord =~ /^($nprep)($art)(ⲉⲧ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|" . $4;}
			elsif ($_f && $hn_ && $strWord =~ /^($nprep)($art)(ⲉⲧ)($pprep)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif ($hn_ && $strWord =~ /^($nprep)($art)(ⲉⲧ)(ⲛⲁ)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|" . $4 . "|" . $5;}
			#presentative
			elsif ($strWord =~ /^(ⲉⲓⲥ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲉⲓⲥ)$/o) {$strWord = $1 . "|" . $2;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲉⲓⲥ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}

			#tripartite clause
			#pronominal
			elsif ($tri_  && $strWord =~ /^($triprobase)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif ($_f && $strWord =~ /^($triprobase)($ppers)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#COMPOUND elsif ($tri_  && $strWord =~ /^($triprobase)($ppers)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($tri_  && $strWord =~ /^($triprobase)($ppers)($verblist)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			#2sgF
			elsif ($strWord =~ /^(ⲁⲣ)($verblist)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif ($_f && $strWord =~ /^(ⲁⲣ)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3;}
			#COMPOUND elsif ($strWord =~ /^(ⲁⲣ)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 ;}
			elsif ($strWord =~ /^(ⲁⲣ)($verblist)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#proper name subject
			#elsif ($tri_  && $strWord =~ /^($trinbase)($namelist)($verblist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3;}
			#elsif ($_f && $tri_  && $strWord =~ /^($trinbase)($namelist)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#elsif ($tri_  && $strWord =~ /^($trinbase)($namelist)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ;}
			#prenominal
			#elsif ($tri_  && $strWord =~ /^($trinbase)($art|$ppos)($nounlist)($verblist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#elsif ($_f && $tri_  && $strWord =~ /^($trinbase)($art|$ppos)($nounlist)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#elsif ($tri_  && $strWord =~ /^($trinbase)($art|$ppos)($nounlist)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#proper name subject separate bound group
			elsif ($tri_  && $strWord =~ /^($trinbase)($namelist)$/o)  {$strWord = $1 . "|" . $2;}
			#prenominal separate bound group
			elsif ($tri_  && $strWord =~ /^($trinbase)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3;}

			#with je-
			#pronominal
			elsif ($je_ && $strWord =~ /^(ϫⲉ)($triprobase)($ppers)($verblist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($je_ && $_f && $strWord =~ /^(ϫⲉ)($triprobase)($ppers)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#COMPOUND elsif ($je_ && $strWord =~ /^(ϫⲉ)($triprobase)($ppers)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)($triprobase)($ppers)($verblist)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 ."|" . $6;}
			#2sgF
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲁⲣ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif ($je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲁⲣ)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#COMPOUND elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲁⲣ)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲁⲣ)($verblist)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			#proper name subject
			#elsif ($je_ && $strWord =~ /^(ϫⲉ)($trinbase)($namelist)($verblist)$/)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#elsif ($je_ && $_f && $strWord =~ /^(ϫⲉ)($trinbase)($namelist)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#elsif ($je_ && $strWord =~ /^(ϫⲉ)($trinbase)($namelist)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#prenominal
			#elsif ($je_ && $strWord =~ /^(ϫⲉ)($trinbase)($art|$ppos)($nounlist)($verblist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#elsif ($je_ && $_f && $strWord =~ /^(ϫⲉ)($trinbase)($art|$ppos)($nounlist)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6;}
			#elsif ($je_ && $strWord =~ /^(ϫⲉ)($trinbase)($art|$ppos)($nounlist)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6;}
			#proper name subject separate bound group
			elsif ($je_ && $strWord =~ /^(ϫⲉ)($trinbase)($namelist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3;}
			#prenominal separate bound group
			elsif ($je_ && $strWord =~ /^(ϫⲉ)($trinbase)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}

			
			#Verboids
			#pronominal subject - peja=f, nanou=s
			elsif ($_f && $strWord =~ /^($vbdlist)($ppero)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif ($_f && $strWord =~ /^(ⲛ|ⲙ)($vbdlist)($ppero)$/o) {$strWord = $1 . "|" . $2  . "|" . $3;} #negated
			elsif ($je_ && $_f && $strWord =~ /^(ϫⲉ)($vbdlist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" .$3  ;} #with je
			elsif ($je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ)($vbdlist)($ppero)$/o) {$strWord = $1 . "|" . $2  . "|" . $3. "|" .$4;} #negated with je
			elsif ($_f && $strWord =~ /^(ⲉⲧ?|ⲛ?ⲉⲣⲉ)($vbdlist)($ppero)$/o) {$strWord = $1 . "|" . $2. "|" . $3 ;} # converted
			
			#nominal subject - peje-prwme
			#elsif ($strWord =~ /^($vbdlist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif ($strWord =~ /^($vbdlist)($namelist)$/o) {$strWord = $1 . "|" . $2 ;}
			
			#bipartite clause
			#pronominal + future
			elsif ($strWord =~ /^($bibase)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2;}
			elsif ($strWord =~ /^(ⲛ|ⲙ)($bibase)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2."|".$3;} #negated
			elsif ($strWord =~ /^($bibase)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif ($_f && $strWord =~ /^($bibase)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4;}
			elsif ($strWord =~ /^($bibase)(ⲛⲁ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5;}
			elsif ($strWord =~ /^($art|$ppos)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($_f && $strWord =~ /^($art|$ppos)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|".$5;}
			elsif ($strWord =~ /^(ⲛ|ⲙ)($bibase)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4;} #negated
			elsif ($_f && $strWord =~ /^(ⲛ|ⲙ)($bibase)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4. "|" . $5;}#negated
			elsif ($strWord =~ /^(ⲛ|ⲙ)($bibase)(ⲛⲁ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5. "|" . $6;}#negated
			elsif ($strWord =~ /^(ⲛ|ⲙ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}#negated
			elsif ($_f && $strWord =~ /^(ⲛ|ⲙ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|".$5. "|" . $6;}#negated
			#indefinite + future
			elsif ($strWord =~ /^($exist)($nounlist)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif ($strWord =~ /^($exist)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($_f && $strWord =~ /^($exist)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;}
			#with je-
			#pronominal + future
			elsif ($je_ && $strWord =~ /^(ϫⲉ)($bibase)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)($bibase)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4;}
			elsif ($je_ && $_f && $strWord =~ /^(ϫⲉ)($bibase)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)($bibase)(ⲛⲁ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5;}
			elsif ($je_ && $_f && $strWord =~ /^(ϫⲉ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ)($bibase)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ)($bibase)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4. "|".$5;}
			elsif ($je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ)($bibase)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5. "|".$6;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ)($bibase)(ⲛⲁ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6. "|".$7;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5. "|".$6;}
			elsif ($je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲛ|ⲙ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)($ppero)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6. "|".$7;}
			#indefinite + future
			elsif ($je_ && $strWord =~ /^(ϫⲉ)($exist)($nounlist)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)($exist)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3. "|".$4 . "|" . $5;}
			elsif ($je_ && $_f && $strWord =~ /^(ϫⲉ)($exist)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|". $6;}
			
			#converted bipartite clause
			#pronominal + future
			elsif ($strWord =~ /^(ⲉⲧ?|ⲛⲉ)($ppers)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif ($_f && $strWord =~ /^(ⲉⲧ?|ⲛⲉ)($ppers)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;}
			elsif ($strWord =~ /^(ⲉⲧ?|ⲛⲉ)($ppers)($nprep)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;} #PP predicate
			elsif ($strWord =~ /^(ⲉⲧ?|ⲛⲉ)($ppers)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($_f && $strWord =~ /^(ⲉⲧ?|ⲛⲉ)($ppers)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;}
			#nominal
			elsif ($strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif ($_f && $strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6;}
			elsif ($strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			#indefinite
			elsif ($strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛⲉ)($exist)($nounlist)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛⲉ)($exist)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif ($_f && $strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛⲉ)($exist)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5. "|".$6;}
			elsif ($strWord =~ /^(ⲉ(?:ⲧⲉ)?|ⲛⲉ)($exist)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			#with je-
			#pronominal + future
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉ)($ppers)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉ)($ppers)($nprep)($art)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6;} #PP predicate
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉ)($ppers)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;}
			elsif ($je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉ)($ppers)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6;}
			#nominal
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)($verblist|$vstatlist|$advlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6;}
			elsif ($je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6."|".$7;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#indefinite
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉ)($exist)($nounlist)($verblist|$vstatlist|$advlist)$/){$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4."|".$5;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉ)($exist)($nounlist)(ⲛⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6;}
			elsif ($je_ && $_f && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉ)($exist)($nounlist)(ⲛⲁ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5."|".$6."|".$7;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲛ?ⲉ)($exist)($nounlist)$/){$strWord = $1 . "|" . $2 . "|" . $3 ."|".$4;}
			
			#interlocutive nominal sentence
			elsif ($strWord =~ /^($pperinterloc)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2  . "|" . $3 ;}
			elsif ($strWord =~ /^($pperinterloc)($namelist)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif ($strWord =~ /^(ⲛ)($pperinterloc)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2  . "|" . $3. "|" . $4 ;}
			elsif ($strWord =~ /^(ⲛ)($pperinterloc)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)($pperinterloc)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)($pperinterloc)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲛ)($pperinterloc)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲛ)($pperinterloc)($namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			
			
			#simple NP - moved from before "relative generic NP p-et-o, ... " to account for preterite ne|u-sotm instead of possessive *neu-sotm with nominalized verb
			#if this causes trouble consider splitting ART and PPOS cases of simple NP
			elsif ($strWord =~ /^(ⲛϭⲓ|ϫⲉ|ϫⲓⲛ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif ($strWord =~ /^($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif ($strWord =~ /^([ⲡⲧⲛ]ⲁ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ;}
			elsif ($strWord =~ /^(ⲛ|ⲙ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ;}
			elsif ($strWord =~ /^(ⲛ|ⲙ)([ⲡⲧⲛ]ⲁ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($strWord =~ /^(ⲛϭⲓ|ϫⲉ|ϫⲓⲛ)($namelist)$/o) {$strWord = $1 . "|" . $2 ;}

			#nominal separated future verb or independent/to-infinitive
			elsif($_f && $strWord =~ /^($verblist)($ppero)$/){$strWord = $1 . "|" . $2;}
			elsif($strWord =~ /^(ⲛⲁ|ⲉ)($verblist)$/){$strWord = $1 . "|" . $2;}
			elsif($strWord =~ /^(ⲛⲁ|ⲉ)($verblist)($ppero|$namelist)$/){$strWord = $1 . "|" . $2 . "|" . $3;}
			#COMPOUND elsif($strWord =~ /^(ⲛⲁ|ⲉ)($verblist)($nounlist)$/){$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif($strWord =~ /^(ⲛⲁ|ⲉ)($verblist)($art|$ppos)($nounlist)$/){$strWord = $1 . "|" . $2 . "|" . $3."|".$4;}

			#converted tripartite clause
			#pronominal
			elsif ($strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)($triprobase)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($_f && $strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)($triprobase)($ppers)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			#COMPOUND elsif ($strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)($triprobase)($ppers)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif ($strWord =~ /^($art)(ⲉⲛⲧ)(ⲁ)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;} #nominalized
			elsif ($_f && $strWord =~ /^($art)(ⲉⲛⲧ)(ⲁ)($ppers)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;} #nominalized
			elsif ($strWord =~ /^($art)(ⲉⲛⲧ)(ⲁⲣ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;} #nominalized
			elsif ($_f && $strWord =~ /^($art)(ⲉⲛⲧ)(ⲁⲣ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;} #nominalized
			#prenominal
			elsif ($strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)$/)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			#elsif ($strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)($verblist)$/)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#elsif ($_f && $strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)($verblist)($ppero)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5. "|".$6;}
			#elsif ($strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)($verblist)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5. "|".$6;}
			elsif ($strWord =~ /^($art)(ⲉⲛⲧ)(ⲁ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}  #nominalized
			#elsif ($strWord =~ /^($art)(ⲉⲛⲧ)(ⲁ)($art|$ppos)($nounlist)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5. "|" . $6;}  #nominalized
			#proper name subject separate bound group
			elsif ($strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)(ⲁ|ⲛⲛⲉ)($namelist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3;}
			#prenominal separate bound group
			elsif ($strWord =~ /^(ⲉ?ⲛⲧ|ⲉ)(ⲁ|ⲛⲛⲉ)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			## With conjunction
			#pronominal
			elsif ($strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($ppers)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5;}
			elsif ($_f && $strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($ppers)($verblist)($ppero)$/)  {$strWord =  $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6}
			#COMPOUND elsif ($strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($ppers)($verblist)($nounlist)$/)  {$strWord =  $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;}
			elsif ($strWord =~ /^(ϫ[ⲉⲓ])($art)(ⲉⲛⲧ)(ⲁ)($ppers)($verblist)$/) {$strWord =  $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;} #nominalized
			elsif ($_f && $strWord =~ /^(ϫ[ⲉⲓ])($art)(ⲉⲛⲧ)(ⲁ)($ppers)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6 . "|". $7;} #nominalized
			elsif ($strWord =~ /^(ϫ[ⲉⲓ])($art)(ⲉⲛⲧ)(ⲁⲣ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;} #nominalized
			elsif ($_f && $strWord =~ /^(ϫ[ⲉⲓ])($art)(ⲉⲛⲧ)(ⲁⲣ)($verblist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;} #nominalized
			#prenominal
			elsif ($strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)$/o)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			#elsif ($strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)($verblist)$/)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5. "|".$6;}
			#elsif ($_f && $strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)($verblist)($ppero)$/)  {$strWord =  $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6 . "|". $7;}
			#elsif ($strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)($verblist)($nounlist)$/)  {$strWord =  $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6 . "|". $7;}
			elsif ($strWord =~ /^(ϫ[ⲉⲓ])($art)(ⲉⲛⲧ)(ⲁ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6;}  #nominalized
			#elsif ($strWord =~ /^(ϫ[ⲉⲓ])($art)(ⲉⲛⲧ)(ⲁ)($art|$ppos)($nounlist)($verblist)$/) {$strWord =  $1 . "|" . $2 . "|" . $3 . "|" . $4. "|" . $5 . "|" . $6 . "|". $7;}  #nominalized
			#proper name subject separate bound group
			elsif ($strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($namelist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3. "|" . $4;}
			#prenominal separate bound group
			elsif ($strWord =~ /^(ϫ[ⲉⲓ])(ⲉ?ⲛⲧ|ⲉ)($triprobase)($art|$ppos)($nounlist)$/o)  {$strWord = $1 . "|" . $2 . "|" . $3. "|" . $4 . "|" . $5;}
			#1sgConjunctive - if nta- didn't match converted past
			elsif ($strWord =~ /^(ⲛ)(ⲧⲁ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif ($strWord =~ /^(ⲛ)(ⲧⲁ)($verblist)($ppero|$namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ."|". $4;}
			elsif ($strWord =~ /^(ⲛ)(ⲧⲁ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ."|". $4."|".$5;}
			#jin|nt|a|S|V|O
			elsif ($strWord =~ /^(ϫⲓⲛ)(ⲛⲧ)(ⲁ)($ppers)($verblist)$/o)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			elsif ($strWord =~ /^(ϫⲓⲛ)(ⲛⲧ)(ⲁ)($ppers)($verblist)($ppero)$/o)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5 . "|" . $6;}
			elsif ($strWord =~ /^(ϫⲓⲛ)(ⲛⲧ)(ⲁ)($art|$ppos)($nounlist)$/o)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 ."|" . $5;}
			elsif ($strWord =~ /^(ϫⲓⲛ)(ⲛⲧ)(ⲁ)($namelist)$/o)   {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			
			
			#possessives
			elsif ($strWord =~ /^((?:ⲟⲩⲛⲧ|ⲙⲛⲧ)[ⲁⲉⲏ]?)($ppers)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif ($strWord =~ /^((?:ⲟⲩⲛⲧ|ⲙⲛⲧ)[ⲁⲉⲏ]?)($ppers)$/o) {$strWord = $1 . "|" . $2 ;}
			elsif ($strWord =~ /^(ⲛⲉ|ⲉ)((?:ⲟⲩⲛⲧ|ⲙⲛⲧ)[ⲁⲉⲏ]?)($ppers)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3."|".$4;}
			elsif ($strWord =~ /^(ⲛⲉ|ⲉ)((?:ⲟⲩⲛⲧ|ⲙⲛⲧ)[ⲁⲉⲏ]?)($ppers)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ;}

			#IMOD
			elsif ($_f && $strWord =~ /^($imodlist)($ppero)$/o) {$strWord = $1 . "|" . $2;}

			#converter+prep
			elsif ($strWord =~ /^(ⲉⲧ)($indprep)$/o) {$strWord = $1 . "|" . $2;}

			#PP with no article
			elsif ($hn_ && $strWord =~ /^($nprep)($nounlist|$namelist)$/o) {$strWord = $1 . "|" . $2;}
			elsif ($hn_ && $strWord =~ /^(ϫⲉ)($nprep)($nounlist|$namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 ;}

			#negative or quoted imperative
			elsif ($strWord =~ /^(ⲙⲡⲣ|ϫⲉ)($verblist)$/o) {$strWord = $1 . "|" . $2;}
			elsif ($strWord =~ /^(ⲙⲡⲣ|ϫⲉ)($verblist)($ppero|$namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif ($strWord =~ /^(ⲙⲡⲣ|ϫⲉ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($strWord =~ /^(ⲙⲡⲣ|ϫⲉ)($verblist)($nounlist)($ppero)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲙⲡⲣ)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲙⲡⲣ)($verblist)($ppero|$namelist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲙⲡⲣ)($verblist)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|". $5;}

			#tm preposed before subject in negative conjunctive with separated verb
			elsif ($strWord =~ /^(ⲛⲧⲉ)(ⲧⲙ)($nounlist)$/o) {$strWord = $1 . "|" . $2. "|" . $3;}
			
			#p-tre-f-V style NP with or without preposition
			elsif (($hn_ || $je_) && $strWord =~ /^($nprep|ϫⲉ)(ⲡⲉ?|$ppos)(ⲧⲣⲉ)($ppero)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif (($hn_ || $je_) && $strWord =~ /^($nprep|ϫⲉ)(ⲡⲉ?|$ppos)(ⲧⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif ($strWord =~ /^(ⲡⲉ?|$ppos)(ⲧⲣⲉ)($ppero)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲡⲉ?|$ppos)(ⲧⲣⲉ)($ppero)($verblist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			elsif ($strWord =~ /^(ⲡⲉ?|$ppos)(ⲧⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4;}
			elsif ($je_ && $strWord =~ /^(ϫⲉ)(ⲡⲉ?|$ppos)(ⲧⲣⲉ)($art|$ppos)($nounlist)$/o) {$strWord = $1 . "|" . $2 . "|" . $3 . "|" . $4 . "|" . $5;}
			
			#else {			
			#nothing found
			#}	

		#split off negating TMs
		if ($strWord=~/\|ⲧⲙ(?!ⲁⲉⲓⲏⲩ|ⲁⲓⲏⲩ|ⲁⲓⲟ|ⲁⲓⲟⲕ|ⲙⲟ|ⲟ$|\|)/) {$strWord =~ s/\|ⲧⲙ/|ⲧⲙ|/;}
		if ($strWord=~/^$ke_art\|/o) {$strWord =~ s/^([^\|]+)ⲕⲉ\|/$1\|ⲕⲉ\|/;}
		if ($strWord=~/\|$ke_art\|/o) {$strWord =~ s/\|([^\|]+)ⲕⲉ\|/\|$1\|ⲕⲉ\|/;}
		
		# split irregular negation ⲙⲉϣϣⲉ
		$strWord=~ s/\|ⲙⲉϣϣⲉ/|ⲙⲉ|ϣϣⲉ/;
		
		
		$strWord =~ s/^\|//;  # No leading pipes
		$strWord =~ s/\|+/\|/; # No double pipes
		$strWord;
}


sub begins_with
{
    return substr($_[0], 0, length($_[1])) eq $_[1];
}