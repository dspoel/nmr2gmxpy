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
from Dihedral_restraint_list import Dihedral_restraint_list
from Orientation_restraint_list import Orientation_restraint_list
#from Atoms_names_amber import Atoms_names_amber
import Atoms_names_amber


import sys
import os
import argparse

DOWNLOAD_FROM_SERVER = False

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


def make_restraint_file(restraint_type, mr_file, verbose):
    
    
    if restraint_type == "distance":
        res = Distance_restraint_list(mr_file, verbose)
    elif restraint_type == "dihedral":
        res = Dihedral_restraint_list(mr_file, verbose)
    elif restraint_type == "orientation":
        res = Orientation_restraint_list(mr_file, verbose)
    else:
        print("Error: unknown restraint type.")
        print("Restraint type can be: distance, dihedral or orientation")
    
    
    #res.set_verbose(verbose)
    res.replace_atoms_names_and_groups()
    # only for distance
    res.change_units()
#    res.set_type_average(1)

    file_out = mr_file[0:-7] + '_' + restraint_type + '.itp'
    fp = open(file_out, 'w')
    res.write_header_in_file(fp)
    res.write_data_in_file(fp)
    return file_out


def call_restraint_make_function(restraint_type, mr_file, verbose, debug):
    
    try:
        outf = make_restraint_file(restraint_type, mr_file, verbose)
        print("SUCCESS: %s restraints were generated in file '%s'." % (restraint_type,outf))
        return outf;
    except FormatError as ex:
        print("Warning:")
        print(ex)
        print("NO %s restraint file was generated." % restraint_type)
        
        if(debug):
            printException(debug)
    except Exception as ex:
        printException(debug)

def include_in_topfile(filename):
    insert = '#include "' + os.path.basename(filename) + '"'

    val = 0
    lines = []
    with open(args.topfile) as fp:
        for line in fp:
            lines.append(line)
            line = line.rstrip()  # remove '\n' at end of line
            if insert == line: # if the insert is already in the file
                return 
    lines = []
    with open(args.topfile) as fp:
        for number, line in enumerate(fp,1):
            lines.append(line)
            line = line.rstrip()  # remove '\n' at end of line
            if "; Include Position restraint file" == line:
                val = number;

    if val==0:
        print("Warning!")
        print("Cannnot write include in the topology file automatically.\n"
            "You should add this line:\n" + insert + "\nat the end of '" + args.topfile + "'.")
        return
        
    lines.insert(val-1, insert + "\n")

    with open(args.topfile, "w") as fp:
        for line in lines:
            fp.write(line)


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
                         type=str)
    parser.add_argument("-p", "--topfile", help= "GROMACS topology file with .top file name extension.\
                    The current version of the program works only for AMBER and CHARMM force fields.\
                    IMPORTANT:When create topology with pdb2gmx use flag -ignh for proper H names.",
                         type=str)
    parser.add_argument("-v", "--verbose", help="Print information as we go", action="store_true")

    parser.add_argument("-d", "--debug", 
                        help="Print traceback for errors if any. Also print traceback for warnings.",
                         action="store_true")
    parser.add_argument("-n", "--name")
    args = parser.parse_args()
    
    topfile_flag=0
    mrfile_flag=0
    name_flag=0
    
    if args.name!=None:
        name_flag=True
    if args.mrfile!=None:
        mrfile_flag=True
    if args.topfile!=None:
        topfile_flag=True
    
    if name_flag==topfile_flag or name_flag==mrfile_flag:
        print("You should give me either files names or protein name I will download.")
        print(__doc__)
        sys.exit(1);
    
    if name_flag:
        global DOWNLOAD_FROM_SERVER
        DOWNLOAD_FROM_SERVER = True
        return args
    
    if args.mrfile[-3:] != "str":
        print("\tError: NMRstar file should have .str extansion.")
        print(__doc__)
        sys.exit(1);
        
    if args.topfile[-3:] != "top":
        print("\tError: GROMACS topology file should have .top extansion.")
        print(__doc__)
        sys.exit(1);
    
    return args

#================================================================================
# MAIN

args  = parse_arguments()

if DOWNLOAD_FROM_SERVER:
    try:
        errno = os.system("./file_manager_gromacs.py " + args.name)
    except:
        print("error")

    if errno!=0:
        sys.exit(1)

    args.topfile = args.name + ".top"
    args.mrfile = args.name + "_mr.str"

# Reading topology file
Atoms_names_amber.Atoms_names_amber.init_atoms_list(args.topfile)

print("\n~~~~~~DISTANCE RESTRAINTS~~~~~~~")
    
restraint_type = "distance"
filename=call_restraint_make_function(restraint_type, args.mrfile, args.verbose, args.debug)
if filename:
    include_in_topfile(filename)

print("\n~~~~~~~DIHEDRAL RESTRAINTS~~~~~~~")
    
restraint_type = "dihedral"
filename = call_restraint_make_function(restraint_type, args.mrfile, args.verbose, args.debug);
if filename:
    include_in_topfile(filename)
print("\n~~~~~ORIENTATION RESTRAINTS~~~~~")
    
restraint_type = "orientation"
filename = call_restraint_make_function(restraint_type, args.mrfile, args.verbose, args.debug);
if filename:
    include_in_topfile(filename)
print("\ngmx #666: 'It is important to not generate senseless output.' (Anyone who's ever used a computer)")
    


