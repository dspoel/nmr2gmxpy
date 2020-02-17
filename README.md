nmr2gmxpy
=========

This program gets distance, dihedral and orientation restraints from Nuclear Magnetic Resonance (NMR)data files and convert them to GROMACS format.

Cheatsheet
----------
Here are the terms and abbriviation we will use:
* .str - file for NMR restraints V2 (STAR) data. There are other NMR formats with the same extension, but our program works only with this format, where the names of the atoms are the same as in coordinate file. Usually the name of the file is <protein>_mr.str
* .top - file for GROMACS topology. This file can be generated by "gmx dbb2gmx" program from any pdb file. Don't forget that for different force fields topology files are different. Also always use flag "-ignh" to ask GROMACS put correct names for the hydrogens.

The flowchart of the nmr2gmx is presented [here](http://github.com). Remember that it represents the logic, but not the concrete implementation (i.e there is now structure top.atoms and str.atoms). In the flow chart we separated the processes of finding atom number, since it is the most important part of the program. We also explicetly show that if atom names in NMR file are differnt from your force field names, it will case an error. Knowing this fact will reduse your worries when you want to implement look-up-table for another force field (this will be discussed in more details futher). In case you do it wrong, no result will be generated.

Atom_names
----------
In a restraint .itp file, atoms are labeled not by their names but by their ordinal numbers with respect to the whole protein.
However, in a NMR .str file there is no such information. So one of the most important part of this program is to extract the correct ordinal numbers for atoms from their names and residue number. It is where the topology file is needed.

And now we face a new problem.
The default names of atoms used in protein_mr.str file and ones used in force fields (hence in gromacs topology file) can be different. So before we would try to find the atom number by its name and the residue number, we have to replace the "wrong" NMR-data names to "right" force-field-names.

The current release solve this problem for AMBER force field, but allow easy implementation for any other force filed as follow. There is an abstract parent class Atom_names with 3 functions: 
1. read .top file;
2. change the names of atoms if needed;
3. return the correct atom number for .itp file form the name of the atom and the residue ordinal number. 

Functions 1 and 3 are force filed independent and are implemented in the parent class itself. Function 2 should be implemented for every force field in a child class, like it is done in Atoms_names_amber for AMBER force field. Then in the "main function" the correct child class should be used. If in your force field all atom names are the same as in protein_mr.str files then you can use the parent class.


![flow chart](/figures/flowchart2.png)
