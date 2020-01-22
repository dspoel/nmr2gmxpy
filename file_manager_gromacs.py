import sys
import os
import ftplib

import gzip
import shutil

#protein = '2I2J'
protein = "2mv5"
# on ftp server they use lower case names
protein_lowcase = protein.lower()
subfolder = protein_lowcase[1:-1] # two middle characters

folder_str = "/pub/pdb/data/structures/divided/nmr_restraints_v2/" + subfolder
file_strgz = protein_lowcase + "_mr.str.gz"
file_str = protein + "_mr.str"

folder_pdb = "/pub/pdb/data/structures/divided/pdb/" + subfolder
file_pdbgz = "pdb" + protein_lowcase + ".ent.gz"
file_pdb = protein + ".pdb"

def download(folder_name, file_in, file_out):
    # /pub/pdb/data/structures/divided/nmr_restraints_v2/<2 middle character, i.e for 2l8s - l8>
    print("Try to download %s"%file_in)
    try:
        print(ftp.cwd(folder_name))
        ftp.retrbinary("RETR " + file_in ,open(file_out, 'wb').write)
    except ftplib.error_perm as ex:
        print("Oops! Seems there is now NMR data for protein " + protein)
        try:
            os.remove(file_in)
            os.remove(file_out)
        except:
            pass
        sys.exit(1)
    except Exception as ex:
        print("ERROR:")
        print(ex)
        sys.exit(1)


def unzip(file_in, file_out):
    print("Try to unzip %s"%file_in)
    try:
        with gzip.open(file_in, 'rb') as f_in:
            with open(file_out, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    except Exception as ex:
        print(ex)
        exit(1)
SERVER_NAME = 'ftp.rcsb.org'
# Connect to RCSB PDB (US) ftp server
print("Triying to connect to the server %s"%SERVER_NAME)
print("Server message:=================================")
try:
    ftp = ftplib.FTP(SERVER_NAME)
    print(ftp.login(user='anonymous', passwd='', acct=''))
    print(ftp.getwelcome())
except Exception as ex:
    print("ERROR:")
    print(ex);
    sys.exit(1);
print("================================================")


download(folder_str, file_strgz, file_strgz)
unzip(file_strgz, file_str)
print("SUCCESS")
os.remove(file_strgz)

download(folder_pdb, file_pdbgz, file_pdbgz)
unzip(file_pdbgz, file_pdb)
print("SUCCESS")
os.remove(file_pdbgz)

#unzip(file_strgz, file_str)
file_top = protein + ".top"
command_line = "gmx -quiet pdb2gmx -f " + file_pdb +  " -ignh -ff amber99sb-ildn -water tip3p -p " + file_top
print("Run:\n\t" + command_line)
try:
    print("=============GROMACS output: ==============================================")
    os.system(command_line)
    print("=============END of GROMACS output ========================================")
    print("SUCCESS")
except Exception as ex:
    print(ex)
