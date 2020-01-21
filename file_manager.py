import sys
from ftplib import FTP

#protein = '2I2J'
protein = "2L8S"
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
    print("Try to download %s"%file_out)
    try:
        print(ftp.cwd(folder_name))
        ftp.retrbinary("RETR " + file_in ,open(file_out, 'wb').write)
    except Exception as ex:
        print("ERROR:")
        print(ex)
        return
    print("SUCCESS")

SERVER_NAME = 'ftp.rcsb.org'
# Connect to RCSB PDB (US) ftp server
print("Triying to connect to the server %s"%SERVER_NAME)
print("Server message:")
try:
    ftp = FTP(SERVER_NAME)
    print(ftp.login(user='anonymous', passwd='', acct=''))
    print(ftp.getwelcome())
except Exception as ex:
    print("ERROR:")
    print(ex);
    sys.exit(1);


download(folder_str, file_strgz, file_str)
download(folder_pdb, file_pdbgz, file_pdb)
#unzip(file_strgz, file_str)