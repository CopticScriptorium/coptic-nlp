import subprocess, io, os

#infile =

proc = subprocess.Popen(['flookup', '-i','..'+os.sep+'coptic_foma.bin', 'ϣⲉⲓⲧⲉ'], stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)


stdout, stderr = proc.communicate()

print(stdout)