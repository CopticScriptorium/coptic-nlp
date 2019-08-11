This directory contains the files needed to compile a fresh transducer binary for the Foma based normalization module.

To compile a new transducer based on the latest normalization info, make sure that foma binaries for your system are in bin/foma/ and that data/norm_table.tab contains the latest normalization data. Foma binaries are available for **Windows** and **Mac OSX** and will be automatically unzipped when you run coptic_nlp.py. 

If you are running coptic_nlp.py on **Linux**, you will need to compile Foma (which should work):

```
wget https://bitbucket.org/mhulden/foma/downloads/foma-0.9.18.tar.gz
tar -xvzf foma-0.9.18.tar.gz
cd foma-0.9.18/
make
sudo make install
```

When you are ready, run:

```
> python compile_grammar.py
```

A new coptic_foma.bin will be generated in this folder, which should replace the existing coptic_foma.bin in bin/