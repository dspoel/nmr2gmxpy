#!/usr/bin/env python3

#   Copyright 2020 Anna Sinelnikova
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
This script can generate input for running restrained MD using the
GROMACS software (http://www.gromacs.org). There are two modes of operation.
1) the user provides a pdb ID (-n option) after which the script downloads 
the pdb file and data from ftp://ftp.rcsb.org, or
2) the user provides restraint data in a Nuclear Magnetic Resonance 
file (NMRstar format) (-s option) plus a pdb file (-q option).

The script will then process the pdb file to make GROMACS input, read
the NMR data file and generate GROMACS restraint files (itp).
The script will try to generate 3 different include topology (itp) files:
distance restraint, dihedral restraint and orientation restraint, 
dependent on the information available in the NMRstar file.

In order to work properly, mode 1 needs an active internet connection.
Both modes need a working GROMACS installation that is at least version 2019.6.
"""
# System libraries
import sys, os, ftplib, glob
import gzip, shutil, argparse
import linecache, traceback

# For logs
from datetime import datetime

# Our owncode
from nmr2gmxpy_lib.Restraint_list import FormatError
from nmr2gmxpy_lib.Distance_restraint_list import Distance_restraint_list
from nmr2gmxpy_lib.Dihedral_restraint_list import Dihedral_restraint_list
from nmr2gmxpy_lib.Orientation_restraint_list import Orientation_restraint_list
from nmr2gmxpy_lib.Atoms_names_amber import Atoms_names_amber

# Low-level routines
def unzip(file_in, file_out, verbose):
    if verbose:
        print("Try to unzip %s"%file_in)
    try:
        with gzip.open(file_in, 'rb') as f_in:
            with open(file_out, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    except Exception as ex:
        print(ex)
        exit(1)

def download(ftp, folder_name, file_in, file_out, verbose, protein):
    # /pub/pdb/data/structures/divided/nmr_restraints_v2/<2 middle character, i.e for 2l8s - l8>
    if verbose:
        print("Try to download %s"%file_in)
    try:
        message = ftp.cwd(folder_name)
        if verbose:
            print(message)
        ftp.retrbinary("RETR " + file_in ,open(file_out, 'wb').write)
    except ftplib.error_perm as ex:
        print("Oops! Seems there is no NMR data for protein " + protein)
        try:
            os.remove(file_out)
        except:
            pass
        sys.exit(1)
    except Exception as ex:
        print("ERROR:")
        print(ex)
        sys.exit(1)
        
def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def find_gmx(fatal=True):
    for mpi in [ "_mpi", "" ]:
        for double in [ "_d", ""]:
            gmx = which("gmx" + mpi + double)
            if gmx:
                return gmx
    if fatal:
        print("Can not find a GROMACS executable. Stopping here.")
        exit(1)
    return None

#------------------------EXEPTION PRINTING---------------------------------------

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

#---------------------MD FILE----------------------------------------------------
def create_md_file(topfile):
    md_file = "ADD_THIS_TO_YOUR_MD_FILE.mdp"
    with open (md_file, "w") as fp:
        fp.write("; Created automaticaly for this topology: %s.\n" % topfile)
        fp.write("; Add what is written in this file to your .mdp file for including constraints\n")
        fp.write("; in your MD calculations. Here are listed all the NMR parameters.\n")
        fp.write("; We suggest to not change them unless you know what you are doing.\n")
        fp.write("\n")
        fp.write("; NMR refinement stuff \n")
    return md_file

def write_distance_restraints_in_md_file(md_file):
    with open (md_file, "a") as fp:
        fp.write("; Distance restraints type: No, Simple or Ensemble\n\
disre                    = Simple\n\
; Force weighting of pairs in one distance restraint: Conservative or Equal\n\
disre-weighting          = Conservative\n\
; Use sqrt of the time averaged times the instantaneous violation\n\
disre-mixed              = no\n\
disre-fc                 = 1000\n\
disre-tau                = 0\n\
; Output frequency for pair distances to energy file\n\
nstdisreout              = 0\n\n")

# dihedral constraints counts automatically form juts topology (itp) file.
def write_dihedral_restraints_in_md_file(md_file):
    with open (md_file, "a") as fp:
        fp.write("; Dihedral restraints do not required any parameters. \
It is enough to include them in topology.\n\n")

def write_orientation_restraints_in_md_file(md_file):
    with open (md_file, "a") as fp:
        fp.write("; Orientation restraints: No or Yes\n\
orire                    = Yes\n\
; Orientation restraints force constant and tau for time averaging\n\
orire-fc                 = 0\n\
orire-tau                = 0\n\
orire-fitgrp             = backbone\n\
; Output frequency for trace(SD) and S to energy file\n\
nstorireout              = 100\n\n")

#--------------------------------------------------------------------------------

def make_restraint_file(restraint_type, mr_file, verbose):
    if restraint_type == "distance":
        res = Distance_restraint_list(verbose)
    elif restraint_type == "dihedral":
        res = Dihedral_restraint_list(verbose)
    elif restraint_type == "orientation":
        res = Orientation_restraint_list(verbose)
    else:
        print("Error: unknown restraint type " + restraint_type)
        print("Restraint type can be: distance, dihedral or orientation")
        return None

    res.read_file(mr_file)
    if res.number_of_restraints() > 0:
        res.change_units()
        res.replace_atoms_names_and_groups()

        file_out = mr_file[0:-7] + '_' + restraint_type + '.itp'
        fp = open(file_out, 'w')
        res.write_header_in_file(fp)
        res.write_data_in_file(fp)
        return file_out, res.number_of_restraints()
    else:
        return None, 0


def call_restraint_make_function(restraint_type, mr_file, verbose, debug):
    if verbose:
        print("restraint_type %s mr_file %s" % ( restraint_type, mr_file ))
    try:
        outf, nrestraints = make_restraint_file(restraint_type, mr_file, verbose)
        if outf:
            print("%d %s restraints were generated in file '%s'." % ( nrestraints, restraint_type,outf ) )
        return outf;
    except FormatError as ex:
        if verbose:
            print("Warning:")
            print(ex)
            print("NO %s restraint file was generated." % restraint_type)
        
        if (debug):
            printException(debug)
        sys.exit(1)
    except Exception as ex:
        printException(debug)
        sys.exit(1)

def include_in_topfile(top_file, include_file):
    insert = '#include "' + os.path.basename(include_file) + '"'

    val = 0
    lines = []
    with open(top_file) as fp:
        for line in fp:
            lines.append(line)
            line = line.rstrip()  # remove '\n' at end of line
            if insert == line: # if the insert is already in the file
                return 
    lines = []
    with open(top_file) as fp:
        for number, line in enumerate(fp,1):
            lines.append(line)
            line = line.rstrip()  # remove '\n' at end of line
            if "; Include Position restraint file" == line:
                val = number;

    if val==0:
        print("Warning!")
        print("Cannnot write include in the topology file automatically.\n"
            "You should add this line:\n" + insert + "\nat the end of '" + top_file + "'.")
        return
        
    lines.insert(val-1, insert + "\n")

    with open(top_file, "w") as fp:
        for line in lines:
            fp.write(line)

def check_extension(filetype, filenm, extension):
    if filenm[-3:] != extension:
        print("\tError: %s file (%s) does not have %s extension." % (filetype, filenm, extension))
        print(__doc__)
        sys.exit(1);

#========================COMMAND LINE ARGUMENTS PARSING==========================
# When command line argument parser error occure, the program print --help
class My_argument_parser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

class FileManager():
#    def __init__(self):
        # Do nothing
    def addArguments(self, parser):
        parser.add_argument("-n", "--protein", help = "4-symbol protein databank identifier. The files corresponding to this pdb ID will be downloaded.",
                            type=str)
        parser.add_argument("-s", "--strfile", help = "NMR restraint V2 (STAR) data file\
        with .str file name extension. Usually the name is <protein>_mr.str",
                         type=str)
        parser.add_argument("-q", "--pdbfile", help= "Protein data bank file with .pdb file name extension, corresponding to the NMR star file.",
                         type=str)
#        parser.add_argument("-p", "--topfile", help= "GROMACS topology consistent with the pdb file", type=str)
        FORCE_FIELD = "amber99sb-ildn"
        parser.add_argument("-ff", "--force_field", help="Force field to use. Only AMBER variants will work for now", default=FORCE_FIELD)
        WATER_MODEL = "tip3p"
        parser.add_argument("-water", "--water_model", help="Water model to use. Only AMBER variants will work for now", default=WATER_MODEL)
        parser.add_argument("-v", "--verbose", help="Print information as we go", action="store_true")
        parser.add_argument("-d", "--debug", 
                        help="Print traceback for errors if any. Also print traceback for warnings.",
                         action="store_true")


    def parseArguments(self, parser):
        self.args = parser.parse_args()
        return self.args

    def gromacsCommandLine(self, top_file, gro_file):
        command_line = find_gmx(True) + " pdb2gmx" + " -f " + self.args.protein + ".pdb" + " -p " + top_file + " -o " + gro_file + " -ff " + self.args.force_field + " -water " + self.args.water_model + " -ignh " #-merge all "
    
        if not self.args.verbose:
            command_line += " > /dev/null 2>&1"
        return command_line

    def downloadAndUnzip(self, log):
        # Connect to RCSB PDB (US) ftp server
        SERVER_NAME = 'ftp.rcsb.org'
        if self.args.verbose:
            print("Trying to connect to the server %s" % SERVER_NAME)
            print("Server message:=================================")
        try:
            ftp = ftplib.FTP(SERVER_NAME)
            message = ftp.login(user='anonymous', passwd='', acct='')
            if self.args.verbose:
                print(message)
            message = ftp.getwelcome()
            if self.args.verbose:
                print(message)
        except Exception as ex:
            print("ERROR:")
            print(ex)
            sys.exit(1)
        if self.args.verbose:
            print("================================================")

        # on ftp server they use lower case names
        protein_lowcase = self.args.protein.lower()
        subfolder = protein_lowcase[1:-1] # two middle characters

        # Download NMR data
        folder_str = "/pub/pdb/data/structures/divided/nmr_restraints_v2/" + subfolder
        remote_file_strgz = protein_lowcase + "_mr.str.gz"
        file_strgz = protein_lowcase + "_mr.str.gz"
        file_str = self.args.protein + "_mr.str"
        download(ftp, folder_str, remote_file_strgz, file_strgz, self.args.verbose, self.args.protein)
        unzip(file_strgz, file_str, self.args.verbose)
        if self.args.verbose:
            print("SUCCESS")
        os.remove(file_strgz)

        # Download pdb file
        folder_pdb = "/pub/pdb/data/structures/divided/pdb/" + subfolder
        remote_file_pdbgz = "pdb" + protein_lowcase + ".ent.gz"
        file_pdbgz = "pdb" + protein_lowcase + ".ent.gz"
        file_pdb = self.args.protein + ".pdb"
        download(ftp, folder_pdb, remote_file_pdbgz, file_pdbgz, self.args.verbose, self.args.protein)
        unzip(file_pdbgz, file_pdb, self.args.verbose)
        if self.args.verbose:
            print("SUCCESS")
        os.remove(file_pdbgz)
    
        log.write("\nThe data has been downloaded from the server: %s.\n\n"%SERVER_NAME)

        return file_str, file_pdb

    def runGromacs(self, log, clean_pdb=None):
        #------CALL GROMACS-------------------------------------------------
        if clean_pdb:
            file_pdb = clean_pdb
            in_pdb   = clean_pdb
        else:
            file_pdb = self.args.protein + "_clean.pdb"
            in_pdb   = self.args.protein + ".pdb"
        file_top   = in_pdb[:-3] + "top"
        file_gro   = in_pdb[:-3] + "gro"
        file_posre = in_pdb[:-4] + "_posre.itp"
        # First we produce a pdb file without merging the chains. This leaves
        # the chain labels in the pdb file that are needed to interpret the
        # NMR files.
        command_line = find_gmx(True) + " pdb2gmx" + " -f " + in_pdb + " -p " + file_top + " -ff " + self.args.force_field + " -i " + file_posre + " -water " + self.args.water_model + " -ignh "
    
        try:
            cmds = [ command_line + " -o " + file_pdb, 
                     command_line + " -merge all -o " + file_gro ]
            first = 0
            if clean_pdb:
                first = 1
            for mycmd in range(first,len(cmds)):
                cmd = cmds[mycmd]
                if self.args.verbose:
                    print("Try to run:\n\t" + cmd)
                    print("============= GROMACS output: ==============================================")
                else:
                    cmd += " > /dev/null 2>&1"
                errno = os.system(cmd)
                if errno > 0:
                    raise Exception("ERROR: GROMACS had a problem. Run with -v to get more info.");

                if self.args.verbose:
                    print("============= END of GROMACS output ========================================")
                    print("SUCCESS")
                
                log.write("Call for GROMACS was:\n")
                log.write("%s\n" % cmd)
                if mycmd == 0:
                    rm_file = glob.glob("posre_*_chain*") + glob.glob("%s_*_chain*itp" % file_top[:-4]) + [ file_top, file_posre ]
                    for rmf in rm_file:
                        if os.path.exists(rmf):
                            os.remove(rmf)
        except Exception as ex:
            print(ex)
            sys.exit(1)
        return file_pdb, file_top, file_gro

    def runGromacs2(self, log, in_pdb):
        #------CALL GROMACS-------------------------------------------------
        file_top   = in_pdb[:-4] + ".top"
        file_pdb   = in_pdb[:-4] + "_out.pdb"
        file_posre = in_pdb[:-4] + "_posre.itp"
        command_line = find_gmx(True) + " pdb2gmx" + " -f " + in_pdb + " -p " + file_top + " -o " + file_pdb + " -ff " + self.args.force_field + " -i " + file_posre + " -water " + self.args.water_model + " -ignh -merge all "
    
        if not self.args.verbose:
            command_line += " > /dev/null 2>&1"
        try:
            if self.args.verbose:
                print("Try to run:\n\t" + command_line)
                print("============= GROMACS output: ==============================================")
            errno = os.system(command_line)
            if errno > 0:
                raise Exception("ERROR: GROMACS had a problem. Run with -v to get more info.");

            if self.args.verbose:
                print("============= END of GROMACS output ========================================")
                print("SUCCESS")
                
            log.write("Call for GROMACS:\n");
            log.write(command_line);
        except Exception as ex:
            print(ex)
            sys.exit(1)
        return file_pdb, file_top

def get_gro_natoms(gro_file):
    with open(gro_file, "r") as inf:
        l = inf.readline()
        w = int(inf.readline().strip())
        return w
    
#========================================
# MAIN
if __name__ == "__main__":
    parser  = My_argument_parser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    logfile = "nmr2gmx.log"
    try:
        log = open(logfile, "w")
    except Exception as e:
        print("Could not open log file %s. Error message %s" % ( logfile, e.message ) )
        sys.exit(1)
        
    log.write(datetime.now().strftime("On %d %B %Y at %H:%M:%S"))
    log.write("\n-----------------------------\n")
    manager = FileManager()
    manager.addArguments(parser)
    args    = manager.parseArguments(parser)
    # Check for correct options
    if args.protein:
        if args.verbose:
            print("Will try to download pdb ID %s" % args.protein)
        if args.pdbfile or args.strfile:
            print("Ignoring options given for pdbfile or strfile")
        args.strfile, args.pdbfile = manager.downloadAndUnzip(log)
        clean_pdb, top_file, gro_file = manager.runGromacs(log)
    elif not (args.pdbfile and args.strfile):
        print("Usage error, please read the documentation.")
        print(__doc__)
        exit(1)
    else:
        # Check input file names
        check_extension("MR star", args.strfile, "str")
        check_extension("PDB", args.pdbfile, "pdb")
        clean_pdb, top_file, gro_file = manager.runGromacs(log, args.pdbfile)

    # Reading pdb file to get correct atom names
    natoms = Atoms_names_amber.init_atoms_list(clean_pdb)
    if args.verbose:
        print("There are %d atoms in %s" % ( natoms, clean_pdb ) )
    # Check that the number of atoms matches the gro file. This may
    # seem excessive but can be a problem in case of intermolecular
    # SS bond.
    natom_gro = get_gro_natoms(gro_file)
    if natoms != natom_gro:
        print("Your system likely has intermolecular disulfide bridges")
        print("or other covalent links between chains. Sorry but this")
        print("script can not handle this.")
        exit(1)

    if args.verbose:
        print("\n~~~~~~DISTANCE RESTRAINTS~~~~~~~")
    
    restraint_type = "distance"
    include_file   = call_restraint_make_function(restraint_type, args.strfile,
                                                  args.verbose, args.debug)
    mdp_file = None
    if include_file:
        include_in_topfile(top_file, include_file)
        mdp_file = create_md_file(top_file)
        write_distance_restraints_in_md_file(mdp_file)

    if args.verbose:
        print("\n~~~~~~~DIHEDRAL RESTRAINTS~~~~~~~")
    
    restraint_type = "dihedral"
    include_file = call_restraint_make_function(restraint_type, args.strfile, args.verbose, args.debug);
    if include_file and mdp_file:
        include_in_topfile(top_file, include_file)
        write_dihedral_restraints_in_md_file(mdp_file)

    if args.verbose:
        print("\n~~~~~ORIENTATION RESTRAINTS~~~~~")
    
    restraint_type = "orientation"
    include_file = call_restraint_make_function(restraint_type, args.strfile, args.verbose, args.debug);
    if include_file and mdp_file:
        include_in_topfile(top_file, include_file)
        write_orientation_restraints_in_md_file(mdp_file)
    if not args.verbose:
        os.remove(clean_pdb)
