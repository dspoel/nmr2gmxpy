nmr2gmxpy
=========

This program gets distance, dihedral and orientation restraints from Nuclear Magnetic Resonance (NMR)data files and convert them to GROMACS format.

The package has two programs. The main nmr2gmx and the util file_manager.

Cheatsheet
----------
Here are the terms and abbreviations we will use:
* .pdb - conventional Protein Data Bank file with atoms names and their coordinats of a concrete protein.
* .str - file for NMR restraints V2 (STAR) data. There are other NMR formats with the same extension, but our program works only with this format, where the names of the atoms are the same as in coordinate file. Usually the name of the file is <protein>_mr.str.
* .top - file for GROMACS topology. This file can be generated by "gmx dbb2gmx" program from any pdb file. Don't forget that for different force fields topology files are different. Also always use flag "-ignh" to ask GROMACS put correct names for the hydrogens.

# nmr2gmx

## For User

### Run

There are two ways to run the program. 

1. The most convenient way is to just pass the name of the protein of interset and let the program do the rest.
It will download all nessesary files (you need an internet connection for this). And then it will run GROMACS to create topology file (you need GROMACS; don't forget to do source /usr/local/gromacs/bin/GMXRC before). The command line is:
```
./nmr2gmx -n 1LVZ -v
```
2. Another option is to pass the .str and .top files (see Cheatsheet) directly like this:
```
./nmx2gmx -s 1LVZ/1LVZ.str -t 1LVZ/1LVZ.top -v
```
This can be convenient if you don't have GROMACS installation on the machine or/and no internet connection.

In both cases you can skip verbose flag -v to which allows you to see what is going on during the run. By default (no -v flag is passed) the program does not create any screen output (except errors if any).

For developers there is a debug flag -d which will provide errors traceback. Use it if you modify the library.

### Output

No matter how you run the program, it will do the following:
1. Create files with restraints. It can be distance/dihedral/orientational restraints, depending on what information is provided in the .str file. The names are "<protein>_<restraint>.itp
2. Include these files (or only one) in your .top file.
3. Create an addition to your GROMACS .mdp file (file with parameters for molecular dynamics). Copy what is written in this file and past in you .mdp file.
  
If you run the program using the first method (with name flag -n), then the program creates a new folder with the same name as you pass and all the files go there. This is convenient because you can use this folder to do you further GROMACS simulations. For example, it contains posre.itp (restraints for heavy ions) file which is produced by GROMACS not this program, but which you need to have more precise simulations. The folder structer also allows you to run nmr2gmx over a list of different proteins and don't mix the output.

## For Developer

The flowchart of the nmr2gmx is presented [here](http://github.com). Remember that it represents the logic, but not the concrete implementation (i.e there is now structure top.atoms and str.atoms). In the flow chart we separated the processes of finding atom number, since it is the most important part of the program. We also explicitly show that if atom names in NMR file are different from your force field names, it will case an error. Knowing this fact will reduce your worries when you want to implement look-up-table for another force field (this will be discussed in more details further). In case you do it wrong, no result will be generated.

### Class Atom_names

In a restraint .itp file, atoms are labeled not by their names but by their ordinal numbers with respect to the whole protein.
However, in a NMR .str file there is no such information. So one of the most important part of this program is to extract the correct ordinal numbers for atoms from their names and residue number. It is where the topology file is needed.

And now we face a new problem.
The default names of atoms used in protein_mr.str file and ones used in force fields (hence in gromacs topology file) can be different. So before we would try to find the atom number by its name and the residue number, we have to replace the "wrong" NMR-data names to "right" force-field-names.

The current release solve this problem for AMBER force field, but allow easy implementation for any other force filed as follow. There is an abstract parent class Atom_names with 3 functions: 
1. read .top file;
2. change the names of atoms if needed;
3. return the correct atom number for .itp file form the name of the atom and the residue ordinal number. 

Functions 1 and 3 are force filed independent and are implemented in the parent class itself. Function 2 should be implemented for every force field in a child class, like it is done in Atoms_names_amber for AMBER force field. Then in the "main function" the correct child class should be used. If in your force field all atom names are the same as in protein_mr.str files then you can use the parent class.

# file_manager
file_manager is a util program which can be used as a stand alone program, but also called by nmr2gmx when you use flag -n.
It can do 2 things for you:
1. Download and unzip .str and .pdb file for a concrete protein;
2. Call GROMACS to generate .top file.

## For User
### Run
You can call the file_manager like this:
```
./file_manager -n 1lvz -v
```
to ask it to download 1lvz_mr.str file and 1lvz.pdb file. Flag -v stands for "verbose", so you will see what is going on while runing. By default (no -v flag is passed) there is no output to the screen unless some errors occur.

If you pass GROMACS flag -gmx:
```
./file_manager -n 1lvz -v -gmx
```
GROMACS will be called to create a .top file (if there is an available installation on your computer, otherwise you will see an error message).
The command line for gromacs will be:
```
gmx pdb2gmx -f 1lvz.pdb -ignh -ff amber99sb-ildn -water tip3p -p 1lvz.top -o 1lvz.gro
```
or gmx_mpi if there is no gmx. As you see the force field and water model are fixed. The current version of nmr2gmx program can only support AMBER force fields. The water model can be any, however we recomend to not change these paramenetrs.
But if you are brave enough or you want to implement a new force field go to the Developer area.

### Output
The program generates a folder with protein name and put there .str file, .pdb file and if you use -gmx flag, .top file
## For Developer
Warning: nmr2gmx depends on the API of file_manager. So be very careful if do any changes and read the Developer quide for nmr2gmx.
