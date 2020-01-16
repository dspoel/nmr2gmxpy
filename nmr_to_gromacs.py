#!/usr/bin/env python3

"""
I can take restraint data from Nuclear Magnetic Resonance data 
file (NMRstar) and convert it to GROMACS restraint files (itp).
I also need corresponding GROMACS topology  file to get right atom names.
I will try to generate 3 .itp files: distance restraint,
dihedral restraint and orientation restraint.
Not every NMRstar file has all nessesary information, but I try my best!
"""

from Restraint_list import FormatError
from Distance_restraint_list import Distance_restraint_list
from Torsion_restraint_list import Torsion_restraint_list
from Orientation_restraint_list import Orientation_restraint_list
import test_atomno

import sys
import os
import argparse

#------------------------EXEPTION PRINTING---------------------------------------
import linecache
import traceback

def printException(printTraceback=True,):
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
#--------------------------------------------------------------------------------


def make_restraint_file(restraint_type, mr_file, top_file, verbose):
    # Reading topology file using module test_atomno.py
    test_atomno.get_file(top_file)
    
    if restraint_type == "distance":
        res = Distance_restraint_list(mr_file, verbose)
    elif restraint_type == "torsion":
        res = Torsion_restraint_list(mr_file, verbose)
    elif restraint_type == "orientation":
        res = Orientation_restraint_list(mr_file, verbose)
    else:
        print("Error: unknown restraint type.")
        print("Restraint type can be: distance, torsion or orientation")
    
    
    #res.set_verbose(verbose)
    res.replace_atoms_names_and_groups()
    # only for distance
    res.change_units()
#    res.set_type_average(1)

    file_out = top_file[0:-4] + '_' + restraint_type + '.itp'
    fp = open(file_out, 'w')
    res.write_header_in_file(fp)
    res.write_data_in_file(fp)
    return file_out


def call_restraint_make_function(restraint_type, mr_file, top_file, verbose, debug):
    
    try:
        outf = make_restraint_file(restraint_type, mr_file, top_file, verbose)
        print("SUCCESS: %s restraints were generated in file '%s'." % (restraint_type,outf))
    except FormatError as ex:
        print("Warning:")
        print(ex)
        print("NO %s restraint file was generated." % restraint_type)
        
        if(debug):
            printException(debug)
    except Exception as ex:
        printException(debug)


#========================COMMAND LINE ARGUMENTS PARSING==========================
# When command line argument parser error occure, the program print --help
class My_argument_parser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def parse_arguments():
    #parser = argparse.ArgumentParser()
    parser = My_argument_parser(description=__doc__,
                            formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-m", "--mrfile", help = "NMR star file with .str file name extension.",
                        required=True, type=str)
    parser.add_argument("-p", "--topfile", help= "GROMACS topology file with .top file name extension.\
                    The current version of the program works only for AMBER and CHARMM force fields.\
                    IMPORTANT:When create topology with pdb2gmx use flag -ignh for proper H names.",
                        required=True, type=str)
    parser.add_argument("-v", "--verbose", help="Print information as we go", action="store_true")

    parser.add_argument("-d", "--debug", 
                        help="Print traceback for errors if any. Also print traceback for warnings.",
                         action="store_true")
    
    args = parser.parse_args()
    return args

#================================================================================

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


print("\n~~~~~~DISTANCE RESTRAINTS~~~~~~~")
    
restraint_type = "distance"
call_restraint_make_function(restraint_type, args.mrfile, args.topfile, args.verbose, args.debug);
    
print("\n~~~~~~~TORSION RESTRAINTS~~~~~~~")
    
restraint_type = "torsion"
call_restraint_make_function(restraint_type, args.mrfile, args.topfile, args.verbose, args.debug);

print("\n~~~~~ORIENTATION RESTRAINTS~~~~~")
    
restraint_type = "orientation"
call_restraint_make_function(restraint_type, args.mrfile, args.topfile, args.verbose, args.debug);
    
print("\ngmx #666: 'It is important to not generate senseless output.' (Anyone who's ever used a computer)")
    
print(args)

