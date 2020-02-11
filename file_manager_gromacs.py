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
I will download nmr-star file and pdb file for the protein you give me
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

VERBOSE = False
GROMACS = True
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
    parser.add_argument("-gmx", "--gromacs", help="GROMACS will be called to generate topology file", action="store_true")
    args = parser.parse_args()
    
    return args

#================================================================================

args = parse_arguments();

protein = args.name;
path = protein;
VERBOSE = args.verbose;
GROMACS = args.gromacs;

# on ftp server they use lower case names
protein_lowcase = protein.lower()
subfolder = protein_lowcase[1:-1] # two middle characters

folder_str = "/pub/pdb/data/structures/divided/nmr_restraints_v2/" + subfolder
remote_file_strgz = protein_lowcase + "_mr.str.gz"
file_strgz = path + "/" + protein_lowcase + "_mr.str.gz"
file_str = path + "/" + protein + "_mr.str"

folder_pdb = "/pub/pdb/data/structures/divided/pdb/" + subfolder
remote_file_pdbgz = "pdb" + protein_lowcase + ".ent.gz"
file_pdbgz = path + "/" + "pdb" + protein_lowcase + ".ent.gz"
file_pdb = path + "/" + protein + ".pdb"

file_top = protein + ".top"
file_gro = protein + ".gro"

def download(folder_name, file_in, file_out):
    # /pub/pdb/data/structures/divided/nmr_restraints_v2/<2 middle character, i.e for 2l8s - l8>
    if VERBOSE:
        print("Try to download %s"%file_in)
    try:
        message = ftp.cwd(folder_name)
        if VERBOSE:
            print(message)
        ftp.retrbinary("RETR " + file_in ,open(file_out, 'wb').write)
    except ftplib.error_perm as ex:
        print("Oops! Seems there is now NMR data for protein " + protein)
        try:
            os.remove(file_out)
        except:
            pass

        if DELETE_DIR_RIGHT:
            try:
                os.rmdir(path)
            except:
                pass
        sys.exit(1)
    except Exception as ex:
        print("ERROR:")
        print(ex)
        sys.exit(1)


def unzip(file_in, file_out):
    if VERBOSE:
        print("Try to unzip %s"%file_in)
    try:
        with gzip.open(file_in, 'rb') as f_in:
            with open(file_out, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    except Exception as ex:
        print(ex)
        exit(1)
        


        
SERVER_NAME = 'ftp.rcsb.org'

if __name__ == "__main__":

    
    # Connect to RCSB PDB (US) ftp server
    if VERBOSE:
        print("Triying to connect to the server %s"%SERVER_NAME)
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

    
    # Create directory (if nit exist) where to download the files
    if not os.path.exists(path):
        DELETE_DIR_RIGHT = True
        try:
            os.mkdir(path)
        except Exception as ex:
            print ("ERROR:")
            print(ex)
            sys.exit(1)
    
    download(folder_str, remote_file_strgz, file_strgz)
    unzip(file_strgz, file_str)
    if VERBOSE:
        print("SUCCESS")
    os.remove(file_strgz)

    download(folder_pdb, remote_file_pdbgz, file_pdbgz)
    unzip(file_pdbgz, file_pdb)
    if VERBOSE:
        print("SUCCESS")
    os.remove(file_pdbgz)

#--------------------------CALL GROMACS-------------------------------------------------
    if GROMACS:
        if VERBOSE:
            command_line = "cd " + path + "/; " + "gmx -quiet pdb2gmx -f " + protein \
                        +  ".pdb -ignh -ff amber99sb-ildn -water tip3p -p " + file_top \
                        + " -o " + file_gro
            print("Run:\n\t" + command_line)
        else:
            # make GROMACS to shut up
            command_line = "cd " + path + "/; " +  "gmx -quiet pdb2gmx -f " + protein \
                        +  ".pdb -ignh -ff amber99sb-ildn -water tip3p -p " + file_top \
                        + " -o " + file_gro + " > /dev/null 2>&1"
        try:
            if VERBOSE:
                print("============= GROMACS output: ==============================================")
            
            errno = os.system(command_line)
            # comand not found ERROR
            if errno >1000:
                raise Exception("I cannot find GROMACS.\nMaybe you forget to do 'source /usr/local/gromacs/bin/GMXRC'?")
            # GROMACS ERROR
            elif errno > 0:
                raise Exception();

            if VERBOSE:
                print("============= END of GROMACS output ========================================")
            if VERBOSE:
                print("SUCCESS")
        except Exception as ex:
            print(ex)
