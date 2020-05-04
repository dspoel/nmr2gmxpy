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
    parser.add_argument("-n", "--name", help = "Conventional 4-symbol name for the protein.",
                         type=str, required=True)
    parser.add_argument("-v", "--verbose", help="Print information as we go", action="store_true")
    FORCE_FIELD = "amber99sb-ildn"
    parser.add_argument("-ff", "--force_field", help="Force field to use. Only AMBER variants will work for now", default=FORCE_FIELD)
    WATER_MODEL = "tip3p"
    parser.add_argument("-water", "--water_model", help="Water model to use. Only AMBER variants will work for now", default=WATER_MODEL)
    parser.add_argument("-gmx", "--run_gromacs", help="GROMACS will be called to generate topology file", action="store_true")
    args = parser.parse_args()
    
    return args

#================================================================================

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

def gromacs_command_line(protein, top_file, gro_file, VERBOSE, FORCE_FIELD, WATER_MODEL):
    gmx = find_gmx()
    if not gmx:
        print("Can not find a GROMACS executable. Stopping here.")
        exit(1)

    command_line = gmx + " pdb2gmx"
    command_line += " -f " + protein + ".pdb" + " -p " + top_file + " -o " + gro_file
    command_line += " -ff " + FORCE_FIELD + " -water " + WATER_MODEL + " -ignh -merge all "
    
    if not VERBOSE:
        command_line += " > /dev/null 2>&1"
    return command_line
    
def download_and_unzip(protein, log):
    # Connect to RCSB PDB (US) ftp server
    SERVER_NAME = 'ftp.rcsb.org'
    if VERBOSE:
        print("Trying to connect to the server %s"%SERVER_NAME)
        print("Server message:=================================")
    try:
        ftp = ftplib.FTP(SERVER_NAME)
        message = ftp.login(user='anonymous', passwd='', acct='')
        if VERBOSE:
            print(message)
        message = ftp.getwelcome()
        if VERBOSE:
            print(message)
    except Exception as ex:
        print("ERROR:")
        print(ex)
        sys.exit(1)
    if VERBOSE:
        print("================================================")

    # on ftp server they use lower case names
    protein_lowcase = protein.lower()
    subfolder = protein_lowcase[1:-1] # two middle characters

    # Download NMR data
    folder_str = "/pub/pdb/data/structures/divided/nmr_restraints_v2/" + subfolder
    remote_file_strgz = protein_lowcase + "_mr.str.gz"
    file_strgz = protein_lowcase + "_mr.str.gz"
    file_str = protein + "_mr.str"
    download(ftp, folder_str, remote_file_strgz, file_strgz, VERBOSE, protein)
    unzip(file_strgz, file_str, VERBOSE)
    if VERBOSE:
        print("SUCCESS")
    os.remove(file_strgz)

    # Download pdb file
    folder_pdb = "/pub/pdb/data/structures/divided/pdb/" + subfolder
    remote_file_pdbgz = "pdb" + protein_lowcase + ".ent.gz"
    file_pdbgz = "pdb" + protein_lowcase + ".ent.gz"
    file_pdb = protein + ".pdb"
    download(ftp, folder_pdb, remote_file_pdbgz, file_pdbgz, VERBOSE, protein)
    unzip(file_pdbgz, file_pdb, VERBOSE)
    if VERBOSE:
        print("SUCCESS")
    os.remove(file_pdbgz)
    
    log.write("\nThe data has been downloaded from the server: %s.\n\n"%SERVER_NAME)
    
if __name__ == "__main__":
    args = parse_arguments()
    VERBOSE = args.verbose

    protein = args.name

    # Create directory (if not exist) where to download the files
    if not os.path.exists(protein):
        DELETE_DIR_RIGHT = True
    os.makedirs(protein, exist_ok="True")
    os.chdir(protein)
    
    logfile = "file_manager.log"
    log = open(logfile, "w")
    log.write(datetime.now().strftime("On %d %B %Y at %H:%M:%S"))
    log.write("\n-----------------------------\n")
    
    download_and_unzip(protein, log)
    
    
#--------------------------CALL GROMACS-------------------------------------------------
    
    if args.run_gromacs:
        file_top = protein + ".top"
        file_gro = protein + "_clean.pdb"
        command_line = gromacs_command_line(protein, file_top, file_gro, VERBOSE,
                                            args.force_field, args.water_model)
        try:
            if VERBOSE:
                print("Try to run:\n\t" + command_line)
                print("============= GROMACS output: ==============================================")
            errno = os.system(command_line)
            #print("error number ", errno)
            # GROMACS ERROR
            if errno > 0:
                raise Exception("ERROR: GROMACS had a problem. Run with -v to get more info.");

            if VERBOSE:
                print("============= END of GROMACS output ========================================")
                print("SUCCESS")
                
            log.write("Call for GROMACS:\n");
            log.write(command_line);
        except Exception as ex:
            print(ex)
    log.close()
