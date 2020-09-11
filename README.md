nmr2gmxpy
=========

This program reads distance, dihedral and orientation restraint information
from Nuclear Magnetic Resonance (NMR) data files in the NMR Star format
and converts it into GROMACS format.

## What is in the box:
1. The script nmr2gmx.py which does all the work,
2. Library routines in nmr2gmxpy_lib,
3. A script run_tests.py to run tests
4. Licence file.

## Installation
1. Install the PyNMRSTAR package. You can find that here
https://github.com/uwbmrb/PyNMRSTAR. However, the preferred way of installing  the software is using pip:
```
pip3 install pynmrstar
```
2. Use the nmr2gmx.py script as described below from your working directory.
 
Cheatsheet
----------
Here are the terms and abbreviations used here:
* .pdb - conventional Protein Data Bank file with atoms names and their coordinats of a concrete protein.
* .str - file for NMR restraints V2 (STAR) data. There are other NMR formats with the same extension, but our program works only with this format, where the names of the atoms are the same as in coordinate file. Usually the name of the file is <protein>_mr.str.
* .top - file for GROMACS topology. This file can be generated by "gmx pdb2gmx" program from any pdb file. Don't forget that for different force fields topology files are different. Also always use flag "-ignh" to ask GROMACS put correct names for the hydrogens.

# nmr2gmx.py

## Running

There are two ways to run the program. 

1. The most convenient way is to just pass the pdb code of the protein of interest and let the program do the rest.
It will download all nessesary files (you need an internet connection for this). And then it will run GROMACS to create topology file (you need GROMACS installed in your path, at least version 2019.6). The command line (assuming the script is installed in $INSTALL_DIR) is:
```
$INSTALL_DIR/nmr2gmx.py -n 1D3Z [-v]
```
in which case the output to the terminal looks like
```
5888 distance restraints were generated in file '1D3Z_distance.itp'.
98 dihedral restraints were generated in file '1D3Z_dihedral.itp'.
61 orientation restraints were generated in file '1D3Z_orientation.itp'.
```
and the following files will be generated:
```
1D3Z.gro			1D3Z_distance.itp		ADD_THIS_TO_YOUR_MD_FILE.mdp
1D3Z.pdb			1D3Z_mr.str			nmr2gmx.log
1D3Z.top			1D3Z_orientation.itp
1D3Z_dihedral.itp		1D3Z_posre.itp
```
2. The second option is to pass the .str and .pdb files (see Cheatsheet) directly like this:
```
$INSTALL_DIR/nmr2gmx.py -s 1D3Z_mr.str -q 1D3Z_clean.pdb [-v]
```
This can be convenient if you don't have an internet connection or if your structure is not (yet) in the protein databank. To generate the input pdb file for the above command you need to run GROMACS pdb2gmx command like this:
```
echo 6 1 | gmx pdb2gmx -f 1D3Z.pdb -o 1D3Z_clean.pdb -ignh
```
(the echo command selects the Amber99sb-ildn force field and TIP3P water model). Note that in this case the output file names  change, since they are derived from the  input PDB file. You will instead get:
```
1D3Z_clean.gro			1D3Z_dihedral.itp		1D3Z_orientation.itp
1D3Z_clean.top			1D3Z_distance.itp		ADD_THIS_TO_YOUR_MD_FILE.mdp
1D3Z_clean_posre.itp		1D3Z_mr.str			nmr2gmx.log
```

In both cases you can skip the verbosity flag -v,  which allows you to
see what is going on when running the script. By default (no -v flag
is passed) the program writes the number of restraints of each type to
the screen but does not create any other screen output except for
error messages.

For developers there is a debug flag -d which will provide some error traceback. Use it if you modify the library.

## Output

No matter how you run the program, it will do the following:
1. Create files with restraints. It can be distance/dihedral/orientational restraints, depending on what information is provided in the .str file. The names are "<protein>_<restraint>.itp
2. Include these files (or only one) in your .top file (this is done automatically by default unless something is wrong)
3. Create an addition to your GROMACS .mdp file (file with parameters for molecular dynamics). Copy what is written in this file and past in you .mdp file.

If you run the program using the first method (with name flag -n), then the program creates a new folder with the same name as you pass and all the files go there. This is convenient because you can use this folder to do you further GROMACS simulations. For example, it contains posre.itp (restraints for heavy ions) file which is produced by GROMACS not this program, but which you need to have more precise simulations. The folder structer also allows you to run nmr2gmx.py over a list of different proteins and don't mix the output.

## Testing

There is a simple script that runs tests by downloading pdb files and
NMR data from the protein data bank, processing it by nmr2gmx.py and
then compare the output restraint files to reference data. In addition
the script runs an energy minimization using GROMACS and compares the
output structure to the input structure. Since the energy minimization
is in vacuo the structures may change by up to 0.02 nm.

This testing script is very useful when extending the scripts, since obviously, the reference data should be reproducible if not it is proven to be incorrect. To run:
```shell
% ./run_tests.py
```
which should give something like:
```shell
728 distance restraints were generated in file '2KYB_distance.itp'.
63 dihedral restraints were generated in file '2KYB_dihedral.itp'.
2KYB - Passed
412 distance restraints were generated in file '1LB0_distance.itp'.
9 dihedral restraints were generated in file '1LB0_dihedral.itp'.
1LB0 - Passed
1070 distance restraints were generated in file '2RQJ_distance.itp'.
2RQJ - Passed
<snip>
Warning: cannot find the GROMACS name for chain D residue HIS-134 atom HD1.
Warning: cannot find the GROMACS name for chain D residue HIS-134 atom HD1.
Warning: cannot find the GROMACS name for chain B residue HIS-134 atom HD1.
Warning: cannot find the GROMACS name for chain B residue HIS-134 atom HD1.
8230 distance restraints were generated in file '1Y76_distance.itp'.
356 dihedral restraints were generated in file '1Y76_dihedral.itp'.
1Y76 - Passed
<snip>
```
(the warning above is due to a missing atom in the structure). The
test set contains proteins, RNA and DNA compounds.

# Developer info

## Class Atom_names

In a restraint .itp file, atoms are labeled not by their names but by their ordinal numbers with respect to the whole protein.  However, in a NMR .str file there is no such information. So one of the most important part of this program is to extract the correct ordinal numbers for atoms from their names and residue number.

The default names of atoms used in protein_mr.str files may differ from the ones used in force fields (hence in gromacs files). So before we would try to find the atom number by its name and the residue number, we have to replace the "wrong" NMR-data names by the "right" force-field-names.

The current release solves this problem for the AMBER force field, but it will be easy to implement for any other force field as follow. There is an abstract parent class Atom_names with 3 functions: 
1. read processed .pdb file and make a table of atom names, residues and chain labels
2. change the names of atoms if needed;
3. return the correct atom number for .itp file form the name of the atom and the residue ordinal number. 

Functions 1 and 3 are force field independent and are implemented in
the parent class itself. Function 2 is to be implemented for every
force field.

License
=======

The package is distributed under Apache License 2.0. Read more in LICENSE file.

Citations
=========

A paper about the software is about to be submitted.


[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4019826.svg)](https://doi.org/10.5281/zenodo.4019826)


