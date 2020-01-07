"""
# Use it wisely
"""
import Restraint_list
from Distance_restraint_list import Distance_restraint_list
from Torsion_restraint_list import Torsion_restraint_list
import Orientation_restraint_list
import test_atomno

import sys
import os
import argparse

# for catching errors
import linecache
import traceback

# Exceptions printing
def printException(printTraceback=True):
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('=======================================')
    print ('ERROR ({}, LINE {} "{}"):\n\t{}'.format(filename, lineno, line.strip(), exc_obj))
    if printTraceback:
        print("")
        print(traceback.format_exc())
    print('=======================================\n')
#########

def make_distance_restraint_file(mr_file, top_file, verbose):
    
    # Reading topology file using module test_atomno.py
    test_atomno.get_file(top_file)
    
    res = Distance_restraint_list(mr_file)
    res.replace_atoms_names_and_groups()
    res.check()
    res.change_units()
    res.set_type_average(1)
    
    file_name = top_file[0:-4] + '_distance.itp'
    
    fp = open(file_name, 'w')
    res.write_header_in_file(fp)
    res.write_data_in_file(fp)

def make_torsion_restraint_file(mr_file, top_file, verbose):
    
    # Reading topology file using module test_atomno.py
    test_atomno.get_file(top_file)
    
    res = Torsion_restraint_list(mr_file)
    res.replace_atoms_names_and_groups()
    
    
    file_out = top_file[0:-4] + '_torsion.itp'
    fp = open(file_out, 'w')
    res.write_header_in_file(fp)
    res.write_data_in_file(fp)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mrfile", help = "NMR star file with .str file name extension.",
                        required=True, type=str)
    parser.add_argument("-p", "--topfile", help= "GROMACS topology file with .top file name extension.",
                        required=True, type=str)
    parser.add_argument("-v", "--verbose", help="Print information as we go", action="store_true")

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args  = parse_arguments()
    
    if args.mrfile[-3:] != "str":
        print("\tError: NMRstar file should have .str extansion.")
        print(__doc__)
        sys.exit(1);
        
    if args.topfile[-3:] != "top":
        print("\tError: GROMACS topology file should have .top extansion.")
        print(__doc__)
        sys.exit(1);


    try:
        outf = make_distance_restraint_file(args.mrfile, args.topfile, args.verbose)
        print("Generated distance restraints in %s" % outf)
    except Exception as ex:
        printException();
    
    
    print("I can do more anyway")
    
