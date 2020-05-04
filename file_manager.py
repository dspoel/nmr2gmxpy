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

# stand alone program
# used by nmr2gmx! Be careful when make any changes.

'''
I will download a NMR-STAR file and corresponding pdb file for the pdb-entry you give me
from the server: ftp.rcsb.org.
I can also call gromacs to create the topology file with amber99sb-ildn force field 
and tip3p water model.

I can be used as a stand alone program, but I am also a part of nmr2gmx program.

'''
import sys
import os
import ftplib

import gzip
import shutil

import argparse

# for logs
from datetime import datetime

# DO NOT change this untill you read README!
# will be set to true when/if the dir is created by this script
DELETE_DIR_RIGHT = False

# Low-level routines
def unzip(file_in, file_out, VERBOSE):
    if VERBOSE:
        print("Try to unzip %s"%file_in)
    try:
        with gzip.open(file_in, 'rb') as f_in:
            with open(file_out, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    except Exception as ex:
        print(ex)
        exit(1)

def download(ftp, folder_name, file_in, file_out, VERBOSE, protein):
    # /pub/pdb/data/structures/divided/nmr_restraints_v2/<2 middle character, i.e for 2l8s - l8>
    if VERBOSE:
        print("Try to download %s"%file_in)
    try:
        message = ftp.cwd(folder_name)
        if VERBOSE:
            print(message)
        ftp.retrbinary("RETR " + file_in ,open(file_out, 'wb').write)
    except ftplib.error_perm as ex:
        print("Oops! Seems there is no NMR data for protein " + protein)
        try:
            os.remove(file_out)
        except:
            pass

        if DELETE_DIR_RIGHT:
            try:
                os.chdir("..")
                os.rmdir(protein)
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

def find_gmx():
    for mpi in [ "_mpi", "" ]:
        for double in [ "_d", ""]:
            gmx = which("gmx" + mpi + double)
            if gmx:
                return gmx
    return None


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
        parser.add_argument("-n", "--protein", help = "Conventional 4-symbol name for the protein.",
                            type=str, required=True)
        parser.add_argument("-v", "--verbose", help="Print information as we go", action="store_true")
        FORCE_FIELD = "amber99sb-ildn"
        parser.add_argument("-ff", "--force_field", help="Force field to use. Only AMBER variants will work for now", default=FORCE_FIELD)
        WATER_MODEL = "tip3p"
        parser.add_argument("-water", "--water_model", help="Water model to use. Only AMBER variants will work for now", default=WATER_MODEL)
        parser.add_argument("-gmx", "--run_gromacs", help="GROMACS will be called to generate topology file", action="store_true")

    def parseArguments(self, parser):
        self.args = parser.parse_args()

    def gromacsCommandLine(self, top_file, gro_file):
        gmx = find_gmx()
        if not gmx:
            print("Can not find a GROMACS executable. Stopping here.")
            exit(1)

        command_line = gmx + " pdb2gmx" + " -f " + self.args.protein + ".pdb" + " -p " + top_file + " -o " + gro_file + " -ff " + self.args.force_field + " -water " + self.args.water_model + " -ignh -merge all "
    
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

    def makeWorkingDirectory(self):
        # Create directory (if not exist) where to download the files
        if not os.path.exists(self.args.protein):
            DELETE_DIR_RIGHT = True
        os.makedirs(self.args.protein, exist_ok="True")
        os.chdir(self.args.protein)

    def runGromacs(self, log):
        #------CALL GROMACS-------------------------------------------------
        if self.args.run_gromacs:
            file_top = self.args.protein + ".top"
            file_gro = self.args.protein + "_clean.pdb"
            command_line = self.gromacsCommandLine(file_top, file_gro)
            try:
                if self.args.verbose:
                    print("Try to run:\n\t" + command_line)
                    print("============= GROMACS output: ==============================================")
                errno = os.system(command_line)
                #print("error number ", errno)
                # GROMACS ERROR
                if errno > 0:
                    raise Exception("ERROR: GROMACS had a problem. Run with -v to get more info.");

                if self.args.verbose:
                    print("============= END of GROMACS output ========================================")
                    print("SUCCESS")
                
                log.write("Call for GROMACS:\n");
                log.write(command_line);
            except Exception as ex:
                print(ex)
        
if __name__ == "__main__":
    parser  = My_argument_parser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    with open("file_manager.log", "w") as log:
        log.write(datetime.now().strftime("On %d %B %Y at %H:%M:%S"))
        log.write("\n-----------------------------\n")
        manager = FileManager()
        manager.addArguments(parser)
        manager.parseArguments(parser)
        manager.makeWorkingDirectory()
        manager.downloadAndUnzip(log)
        manager.runGromacs(log)
