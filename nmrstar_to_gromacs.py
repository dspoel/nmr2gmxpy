#!/usr/bin/env python3

# program to retrive the restraints data from file in PDB
# program is designed to generate multiple restraint file for multiplt protein

import os, argparse, shutil, pynmrstar

# pynmrstar module(from BMRB) is used to read restraint data from PDB
import numpy as np

import test_atomno
#"test_atomno" is a python module which has functions "get_file" and 
#"get_atomno" ; test_atomno uses module "mdjoy" to read a topology file

from operator import itemgetter, attrgetter

### ADDED

import Restraint
import Distance_restraint
import Distance_restraint_list
# for catching errors

import linecache
import sys
import traceback

def printException(printTraceback=True):
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('=======================================')
    print ('EXCEPTION IN ({}, LINE {} "{}"):\n\t{}'.format(filename, lineno, line.strip(), exc_obj))
    if printTraceback:
        print(traceback.format_exc())
    print('=======================================\n')
#########

def dist_restraints(mr_file, top_file, verbose):

    # Reading topology file using module test_atomno.py
    test_atomno.get_file(top_file)
    
    # Patch the parser
    from monkeypatch import patch_parser, unpatch_parser
    patch_parser(pynmrstar)

    # Check if there is a restraint file in the PDB
    exists = os.path.isfile(mr_file)
    if exists:
         entry = pynmrstar.Entry.from_file(mr_file)
    else:
        print("**Error : No NMR restraint file on PDB")
        return None

    # Get Distance Restraints from the file and
    # store them into DR_result_sets
    DR_result_sets = []
    for distance_restraints_loop in entry.get_loops_by_category("_Gen_dist_constraint") :
        DR_result_sets.append(distance_restraints_loop.get_tag(['ID','Auth_seq_ID_1' ,'Atom_ID_1','Comp_ID_1', 'Auth_seq_ID_2','Atom_ID_2' ,'Comp_ID_2','Distance_lower_bound_val','Distance_upper_bound_val'])) 

    # Restore the original parser .. recall we patched the parser before.
    unpatch_parser(pynmrstar)

    # Assigning protein name to new gromacs restraints file
    disres_file = top_file[0:-4] + '_disres.itp'
    
    # Open the file to write it like following format
    f1 = open(disres_file, 'w')
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

    # Convert the array to numpy array
    DR_array = np.array( DR_result_sets)
    
    
    
    
    # Checking if it has correct format!
    # If number of lines is 0 cause error
    if DR_array.shape == (0,): 
        print("**Format Error : Different NMR restraint format for PDB id : " , file_nm)
        # If it has different format then remove it 
        os.remove(dist_res_file) 
        return None
    print("shape",DR_array.shape)
    # Zeroth "line" dimension
    DR_array_0 = np.array(DR_array[0,])
    if verbose:
        print("The dimension of the array: ",DR_array.shape)
        print("The first (zeroth) 'line' dimension: ", DR_array_0.shape)
    
    total = DR_array_0.shape[0]
    if verbose:
        print(total)
    index = 0
    print(DR_array_0[0,]);
    print(DR_array_0[55,])
    
    restraint = Distance_restraint.Distance_restraint(DR_array_0[0,]);
    #restraint.init(DR_array_0[0,]);
    #print (restraint.id);
    #print (restraint.atom_id_1);
    restraint.print_all();
    
    drl = Distance_restraint_list.Distance_restraint_list(mr_file);
    drl.restraints[0].print_all();
    #restraints = Restraint.init_with_NMR_file(mr_file)
    #print (restraint.id);
    #print (restraint.atom_id_1);
    #restraints[0].print_all();
    #restraints[55].print_all();
    
    
    
    f1.write(";    ai\t    aj\t  type\t index\t type'\t   low\t   up1\t   up2\t   fac\n\n")
    for i in range(total):
        #replacing atom names by using atoms names and residue names 
        #and assigns nuber of hydogens in the ME_group1 and ME_group2
        #for example, ME_group1 = 3 if methyle group, 2 if methylene group and 1 if methine group 
        # for more info see test_atomno.py
        DR_array_0[i,2],ME_group1 = test_atomno.atom_replace(DR_array_0[i,2],DR_array_0[i,3])
        DR_array_0[i,5],ME_group2 = test_atomno.atom_replace(DR_array_0[i,5],DR_array_0[i,6])
        # Checking for some errors, like no distance upper bound, no distance lower bound or both
        if DR_array_0[i,8] == '.' :
            print("**Error : No distance upper bound in NMR restraints file for PDB id : ", file_nm)
            os.remove(dist_res_file)
            return None            
        if DR_array_0[i,7] == '.' :
            print("**Error : No distance lower bound in NMR restraints file for PDB id : ", file_nm)
            os.remove(dist_res_file)
            return None    

        if DR_array_0[i,8] == '.' and  DR_array_0[i,7] == '.' :
            print("**Error : No distance lower bound and distance upper bound in NMR restraints file for PDB id : ", file_nm)
            os.remove(dist_res_file)
            return None
        

        # Change distances angstrom to nanometer
        DR_array_0[i,7] = round(float(DR_array_0[i,7])*0.10,2)
        DR_array_0[i,8] = round(float(DR_array_0[i,8])*0.10,2)
        up2 = round(float( DR_array_0[i,8])+0.1,2)
        
        # 1 - for time and ensemble average and
        # 2 - for no time and ensemble average
        type_avg = 1

        # This loop extract the atom numbers from atom names in 
        # the topology file.
        for p in range(ME_group1):
            for q in range(ME_group2):
                current_atom1 = DR_array_0[i,2]
                current_atom2 = DR_array_0[i,5]
                if ME_group1 == 3 or ME_group1 == 2:
                    current_atom1 = current_atom1 + str(p+1)
                if ME_group2 == 3 or ME_group2 == 2:    
                    current_atom2 = current_atom2 + str(q+1)
                
                # For residue number and atom name(current_atom1,current_atom2)
                # find atom number from 2lv8.top 
                # and assign it to ai(atom_no1) and aj(atom_no2)
                atom_no1 = test_atomno.get_atomno(int(DR_array_0[i,1]),current_atom1)
                atom_no2 = test_atomno.get_atomno(int(DR_array_0[i,4]),current_atom2)
                fac = 1.0 # assign value for force constant
                f1.write("%6s\t%6s\t     1\t%6d\t%6d\t%6s\t%6s\t%6s\t%6s\n" %(atom_no1,atom_no2,index,type_avg,DR_array_0[i,7],DR_array_0[i,8],up2,fac))
        # If loop gives information about incorrect format of NMR restraint file : 
        # if first element is zero then file has incorrect format!
        if i == 0 :
            if atom_no1 == 0 :
                print("**Format Error : different residue number in NMR restraint file for PDB id : %s" %file_nm)
                os.remove(dist_res_file)
                return None
        index = index + 1
    f1.close()
    return disres_file


def torsional_restraints(mr_file, top_file, verbose):

    # Read topology file 
    test_atomno.get_file(top_file)
    
    # Patch the parser
    from monkeypatch import patch_parser, unpatch_parser
    patch_parser(pynmrstar)

    # Check if there is a restraint file in the PDB
    exists = os.path.isfile(mr_file) 
    if exists:
         entry = pynmrstar.Entry.from_file(mr_file)
    else:
        print("**Error : No NMR restraint file on PDB")
        return None
    
    # Getting Torsional Restraints
    TR_result_sets = []
    for torsional_restraints_loop in entry.get_loops_by_category("_Torsion_angle_constraint"):
        TR_result_sets.append(torsional_restraints_loop.get_tag(['ID','PDB_residue_no_1','Comp_ID_1', 'Atom_ID_1','PDB_residue_no_2', 'Comp_ID_2','Atom_ID_2','PDB_residue_no_3','Comp_ID_3', 'Atom_ID_3','PDB_residue_no_4','Comp_ID_4', 'Atom_ID_4', 'Angle_lower_bound_val','Angle_upper_bound_val']))

    # Restore the original parser
    unpatch_parser(pynmrstar)

    tor_res_file = top_file[0:-4] + '_dihres.itp'
    g= open(tor_res_file, 'w')

    g.write(";    ai\t    aj\t    ak\t    al\t  type\t   phi\t  dphi\t   fac\n\n")
    TR_array = np.array(TR_result_sets)
    if TR_array.shape == (0,):
        print("**Error : No torsional restraints for PDB id : " , mr_file)#, file_nm)
        os.remove(tor_res_file)
        return None
    TR_array_0 = np.array(TR_array[0,] )
    if verbose:
        print("TR_array : ", TR_array.shape )
        print("TR_array_0 :",TR_array_0.shape)
    total_TR = TR_array_0.shape[0]
    for i in range(total_TR):
         #replacing atom names HB3 
        TR_array_0[i,3],g1 = test_atomno.atom_replace(TR_array_0[i,3],TR_array_0[i,2])
        TR_array_0[i,6],g2 = test_atomno.atom_replace(TR_array_0[i,6],TR_array_0[i,5])
        TR_array_0[i,9],g3 = test_atomno.atom_replace(TR_array_0[i,9],TR_array_0[i,8])
        TR_array_0[i,12],g4 = test_atomno.atom_replace(TR_array_0[i,12],TR_array_0[i,11])
        # g1,g2,g3 and g4 extra output from the fucntion atom_replace in module test_atomno.py
        # getting atom number from residue number and atom name
        atom_1 = test_atomno.get_atomno(int(TR_array_0[i,1]),TR_array_0[i,3])
        atom_2 = test_atomno.get_atomno(int(TR_array_0[i,4]),TR_array_0[i,6])
        atom_3 = test_atomno.get_atomno(int(TR_array_0[i,7]),TR_array_0[i,9])
        atom_4 = test_atomno.get_atomno(int(TR_array_0[i,10]),TR_array_0[i,12])
        phi = round((float(TR_array_0[i,14]) + float(TR_array_0[i,13]))/2.0,2)
        dphi = round((float(TR_array_0[i,14]) - float(TR_array_0[i,13]))/2.0,2)
        fac = 1.0 # assign value for force constant
        g.write("%6s\t%6s\t%6s\t%6s\t     1\t%6s\t%6s\t%6s\n" %(atom_1,atom_2,atom_3,atom_4,phi,dphi,fac))
    g.close()
    # if we created correct torsional restraint file in gromacs format then
    # protein name is placed into 'valid_pdb_id_tor_res.dat' file
    return tor_res_file

def orientation_restraints(mr_file, top_file, verbose):

    # Patch the parser
    from monkeypatch import patch_parser, unpatch_parser
    patch_parser(pynmrstar)

    # Reading topology file 
    test_atomno.get_file(top_file) 

    exists = os.path.isfile(mr_file)
    if exists:
         entry = pynmrstar.Entry.from_file(mr_file)
    else:
        print("**Error : No NMR restraint file on PDB")
        return None

     # Getting Torsional Restraints
    orientation_result_sets = []
    for RDC_restraints_loop in entry.get_loops_by_category("_RDC_constraint"):
        orientation_result_sets.append(RDC_restraints_loop.get_tag(['ID','PDB_residue_no_1','Comp_ID_1', 'Atom_ID_1','PDB_residue_no_2', 'Comp_ID_2','Atom_ID_2','RDC_val']))

    # Restore the original parser
    unpatch_parser(pynmrstar)

    orires_file = top_file[0:-4] + '_orires.itp'
    h= open(orires_file, 'w')

    h.write(";    ai\t    aj\t  type\t  exp.\t label\t alpha\tconst.\t  obs.\tweight\n")
    h.write(";      \t      \t      \t      \t      \t   Hz \t nm^3 \t   Hz \t Hz^-2\n\n")

    orientation_array = np.array(orientation_result_sets)
    if orientation_array.shape == (0,):
        print("**Error : No Orientation restraints for PDB id : " , file_nm)
        os.remove(orientation_res_file)
        return None
    orientation_array_0 = np.array(orientation_array[0,] )
    if verbose:
        print("orientation_array : ", orientation_array.shape )
        print("orientation_array_0 :",orientation_array_0.shape)
    total_orientation = orientation_array_0.shape[0]
    label = 1
    for i in range(total_orientation):
        #replacing atom names 
        orientation_array_0[i,3],g1 = test_atomno.atom_replace(orientation_array_0[i,3],orientation_array_0[i,2])
        orientation_array_0[i,6],g2 = test_atomno.atom_replace(orientation_array_0[i,6],orientation_array_0[i,5])
        atom_1 = test_atomno.get_atomno(int(orientation_array_0[i,1]),orientation_array_0[i,3])
        atom_2 = test_atomno.get_atomno(int(orientation_array_0[i,4]),orientation_array_0[i,6])
        alpha = 3 #assign value for alpha
        const = 6.083 #assign value for constant
        weight = 1.0 # assign value for weight
        type_orientation = 1
        exp = 1
        h.write("%6s\t%6s\t%6s\t%6s\t%6s\t%6s\t%6s\t%6s\t%6s\n" %(atom_1,atom_2,type_orientation,exp,label,alpha,const,orientation_array_0[i,7],weight))
        label = label + 1
    h.close()
    return orires_file

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mrfile", help="NMR star file with .str file name extension.",   type=str,
        default=None)
    parser.add_argument("-p", "--topfile", help="GROMACS topology file.", type=str,
        default=None)
    parser.add_argument("-v", "--verbose", help="Print information as we go", action="store_true")

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args  = parseArguments()
    
    # Find arguments with extention .str and .top (flags were not important?)
    if args.mrfile and args.mrfile[-3:] == "str" and args.topfile and args.topfile[-3:] == "top":

        try:
    	    # Call function dist_restraints() for current file_nm
    	    outf = dist_restraints(args.mrfile, args.topfile, args.verbose)
    	    print("Generated distance restraints in %s" % outf)
        except Exception as ex:
    	    #print("Error in dist_restraints:\n\t", ex)
    	    printException();
#        try:
#	    # Call function torsional_restraints() for current file_nm
#    	    outf = torsional_restraints(args.mrfile, args.topfile, args.verbose) 
#    	    print("Generated dihedral restraints in %s" % outf)
#        except Exception as ex:
#    	    printException();
    	    #print("Error in torsional_restraints:\n\t", ex)
	
#        try:
    	    # Calling function orientation_restraints() for current file_nm
    	    #outf = orientation_restraints(args.mrfile, args.topfile, args.verbose) 
    	    #print("Generated orientation restraints in %s" % outf)
#        except:
#    	    printException();
    	    
    else:
        print("Please give me at a .top file and a .str file")


