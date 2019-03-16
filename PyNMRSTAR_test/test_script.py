#!/usr/bin/env python

# program to retrive the restraints data from file in PDB


import pynmrstar
import numpy as np
import test_atomno

#"test_atomno" is a python module which has functions "get_file" and "get_atomno" ; test_atomno uses module "mdjoy" to read a topology file
test_atomno.get_file('2lv8.top') #reading topology file 

# 2lv8_mr.str is downloaded from PDB website then modified to run into "PyNMRSTAR" module
# first one has to remove the additional contraint file loops as suggested on github(PyNMRSTAR,issues) 
entry = pynmrstar.Entry.from_file('2lv8_mr_edited.str')

entry.print_tree()
#print (entry)

#Getting Distance Restraints 

# reading distance constraints from the file and storing them into DR_result_sets
DR_result_sets = []
for distance_restraints_loop in entry.get_loops_by_category("_Gen_dist_constraint") :
    DR_result_sets.append(distance_restraints_loop.get_tag(['ID','Seq_ID_1' ,'Atom_ID_1','Comp_ID_1', 'Seq_ID_2','Atom_ID_2' ,'Comp_ID_2','Distance_lower_bound_val','Distance_upper_bound_val'])) 

#f=open('2lv8_dist_restraints.dat', 'w')
f1= open('2lv8_modified_dist_rest.dat', 'w')
'''
# ai, aj = the atom numbers of the particles to be restrained
# type = always 1
# index = ---
# type' = 1 , 2 - restraints will never be time and ensemble averaged 
# low = distance lower bound 
# up1 = distance upper bound
# up2 = distance upper bound + 0.1
# fac = 1 for everything
'''


DR_array = np.array( DR_result_sets)
DR_array_0 = np.array(DR_array[0,] )
print(DR_array_0.shape)
total = DR_array_0.shape[0]
print(total)

f1.write("ai\taj\ttype\tindex\ttype'\tlow\tup1\tup2\tfac\n\n")

for i in range(total):
    #for residue id, residue no and atom id find atom no from 2lv8.top and assign it to ai and aj
    atom_no1 = test_atomno.get_atomno(int(DR_array_0[i,1]),DR_array_0[i,2],DR_array_0[i,3])
    atom_no2 = test_atomno.get_atomno(int(DR_array_0[i,4]),DR_array_0[i,5],DR_array_0[i,6])
    up2 =round(float( DR_array_0[i,8])+0.1,2)
    f1.write("%s\t%s\t1\t1\t1\t%s\t%s\t%s\t1.0\n" %(atom_no1,atom_no2,DR_array_0[i,7],DR_array_0[i,8],up2))
f1.close()





