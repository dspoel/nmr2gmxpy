"""
# Use it wisely
"""
from Restraint_list import FormatError
from Distance_restraint_list import Distance_restraint_list
from Torsion_restraint_list import Torsion_restraint_list
from Orientation_restraint_list import Orientation_restraint_list
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
#    res.check()
    res.change_units()
    res.set_type_average(1)
    
    file_name = top_file[0:-4] + '_distance.itp'
    
    fp = open(file_name, 'w')
    res.write_header_in_file(fp)
    res.write_data_in_file(fp)
    return file_name
    

def make_torsion_restraint_file(mr_file, top_file, verbose):
    # Reading topology file using module test_atomno.py
    test_atomno.get_file(top_file)
    
    res = Torsion_restraint_list(mr_file)
    res.replace_atoms_names_and_groups()
    
    
    file_out = top_file[0:-4] + '_torsion.itp'
    fp = open(file_out, 'w')
    res.write_header_in_file(fp)
    res.write_data_in_file(fp)

def make_restraint_file(restraint_type, mr_file, top_file, verbose):
    # Reading topology file using module test_atomno.py
    test_atomno.get_file(top_file)
    
    if restraint_type == "distance":
        res = Distance_restraint_list(mr_file)
    elif restraint_type == "torsion":
        res = Torsion_restraint_list(mr_file)
    elif restraint_type == "orientation":
        res = Orientation_restraint_list(mr_file)
    
    res.replace_atoms_names_and_groups()
    # only for distance
    res.change_units()
#    res.set_type_average(1)

    file_out = top_file[0:-4] + '_' + restraint_type + '.itp'
    fp = open(file_out, 'w')
    res.write_header_in_file(fp)
    res.write_data_in_file(fp)
    return file_out


def call_restraint_make_function(restraint_type, mr_file, top_file, verbose):
    try:
        outf = make_restraint_file(restraint_type, args.mrfile, args.topfile, args.verbose)
        print("Generated %s restraints in '%s'." % (restraint_type,outf))
    except FormatError as ex:
        print("Warning:")
        print(ex)
        print("No %s restraint file was not generated." % restraint_type)
    except Exception as ex:
        printException(False);

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

    print("")

    try:
        outf = make_restraint_file("distance", args.mrfile, args.topfile, args.verbose)
        print("Generated DISTANCE restraints in '%s'" % outf)
    except FormatError as ex:
        print("Warning:")
        print(ex)
        print("DISTANCE restraint file was not generated.")
    except Exception as ex:
        printException(False);
        
    print("")
        
    try:
        outf = make_restraint_file("torsion", args.mrfile, args.topfile, args.verbose)
        print("Generated TORSION restraints in '%s'" % outf)
    except FormatError as ex:
        print("Warning:")
        print(ex)
        print("TORSION restraint file was not generated.")
    except Exception as ex:
        printException(False);
        
    print("")
    
    try:
        outf = make_restraint_file("orientation", args.mrfile, args.topfile, args.verbose)
        print("Generated ORIENTATION restraints in '%s'" % outf)
    except FormatError as ex:
        print("Warning:")
        print(ex)
        print("ORIENTATION restraint file was not generated.")
    except Exception as ex:
        printException(False);
        
        
    print("\ngmx #666: 'It is important to not generate too much senseless output.' (Anyone who ever used computer)")
    
