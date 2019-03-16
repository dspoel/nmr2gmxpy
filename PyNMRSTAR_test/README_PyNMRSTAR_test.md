#mdjoy
A Python module for reading, writing and manipulating topology files and pdb file.

#PyNMRSTAR.py 
A Python module for reading, writing and manipulating NMR-STAR files.

#test_atomno.py
A Python module for reading topology file and returning atom number according to residue number, atom name and residue name.

#test_script.py
A Python program to generate distance restraints file (2lv8_modified_dist_res.dat) 
to execute it write: python3 test_script.py

#2lv8_modified_dist_rest.dat
A data file consisting of distance restraints like gromacs format.
 (ai, aj) = the atom numbers of the particles to be restrained; type = always 1; index = -- ; type' = 1 or 2 - restraints will never be time and ensemble averaged ;
 low = distance lower bound; up1 = distance upper bound;  up2 = distance upper bound + 0.1; fac = 1.0 for every entry

#2lv8_mr_original.str
An original NMR restraint file(V2) downloaded from PDB website for pdb id : "2lv8" 

#2lv8_mr_edited.str
An editted NMR restraint file to use it in PyNMRSTAR module for accessing information regarding restraints.

#2lv8.pdb
A pdb file downloaded from PDB website for pdb id : "2lv8"

#2lv8.top
A topology file generated from 2lv8.pdb by using pdb2gmx for tip3p water, amber99sb-ildn forcefield and ignoring hydrogens for gromacs version 2016.3.

 
