#!/usr/bin/env python

# program to retrive the restraints data from file in PDB

import pynmrstar


# fist you have to remove the additional contraint file loops as suggested on github
entry = pynmrstar.Entry.from_file('2lv8_mr_edited.str')

#entry.print_tree()
#print (entry)

#Getting Distance Restraints 

DR_result_sets = []
for distance_restraints_loop in entry.get_loops_by_category("_Gen_dist_constraint"):
    DR_result_sets.append(distance_restraints_loop.get_tag(['ID','Comp_ID_1', 'Atom_ID_1', 'Atom_type_1', 'Comp_ID_2','Atom_ID_2', 'Atom_type_2', 'Distance_val','Distance_lower_bound_val','Distance_upper_bound_val','PDB_residue_no_1','PDB_residue_name_1','PDB_atom_name_1','PDB_residue_no_2','PDB_residue_name_2','PDB_atom_name_2','Auth_atom_ID_1','Auth_atom_ID_2']))
 

f=open('2lv8_dist_restraints.csv', 'w')
f.write("['iD','Comp_ID_1', 'Atom_ID_1', 'Atom_type_1', 'Comp_ID_2','Atom_ID_2', 'Atom_type_2', 'Distance_val','Distance_lower_bound_val','Distance_upper_bound_val','PDB_residue_no_1','PDB_residue_name_1','PDB_atom_name_1','PDB_residue_no_2','PDB_residue_name_2','PDB_atom_name_2','Auth_atom_ID_1','Auth_atom_ID_2'] \n\n")
for i in DR_result_sets:
    for j in i:
        f.write("%s \n" %j )
f.close()


# Getting Torsional Constraints
TR_result_sets = []
for torsional_restraints_loop in entry.get_loops_by_category("_Torsion_angle_constraint"):
    TR_result_sets.append(torsional_restraints_loop.get_tag(['ID','Seq_ID_1','Comp_ID_1', 'Atom_ID_1', 'Atom_type_1','Seq_ID_2', 'Comp_ID_2','Atom_ID_2', 'Atom_type_2','Seq_ID_3','Comp_ID_3', 'Atom_ID_3', 'Atom_type_3' ,'Seq_ID_4','Comp_ID_4', 'Atom_ID_4', 'Atom_type_4', 'Angle_lower_bound_val','Angle_upper_bound_val']))

g = open('2lv8_tor_restraints.csv', 'w')
g.write("['ID','Seq_ID_1','Comp_ID_1', 'Atom_ID_1', 'Atom_type_1','Seq_ID_2', 'Comp_ID_2','Atom_ID_2', 'Atom_type_2','Seq_ID_3','Comp_ID_3', 'Atom_ID_3', 'Atom_type_3' ,'Seq_ID_4','Comp_ID_4', 'Atom_ID_4', 'Atom_type_4', 'Angle_lower_bound_val','Angle_upper_bound_val'] \n\n")
  
for i in TR_result_sets:
    for j in i:
        #print(j)
        g.write("%s \n" %j )
g.close()







