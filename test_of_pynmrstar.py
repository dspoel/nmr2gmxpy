import pynmrstar

import gzip
import shutil
from ftplib import FTP

ftp = FTP('ftp.rcsb.org')     # connect to host, default port
print(ftp.login(user='anonymous', passwd='', acct=''))
print(ftp.getwelcome()
)

# /pub/pdb/data/structures/divided/nmr_restraints_v2/<2 middle character, i.e for 2l8s - l8>
print(ftp.cwd('/pub/pdb/data/structures/divided/nmr_restraints_v2/l8') )
#print(ftp.retrlines('LIST'))
filename = "2l8s_mr.str.gz"
A = filename
try:
    ftp.retrbinary("RETR " + filename ,open(A, 'wb').write)
except:
    print("error")

#for pdb
#/pub/pdb/data/structures/divided/pdb/l8
#pdb2l8s.ent.gz
strname = filename[:-3];
with gzip.open(filename, 'rb') as f_in:
    with open(strname, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


from monkeypatch import patch_parser, unpatch_parser
patch_parser(pynmrstar)
#entry = pynmrstar.Entry.from_database(17424);
entry = pynmrstar.Entry.from_file("Examples/2L8S_mr.str");
#entry = pynmrstar.Entry.from_file(strname);

#entry1 = pynmrstar.Entry.from_database(17424);
#entry1.write_to_file("output_file.str");
#entry = pynmrstar.Entry.from_file("output_file.str");
unpatch_parser(pynmrstar)
#entry.write_to_file("output_file_name.str")



for loop in entry.get_loops_by_category("_Related_entries"):
    print (loop)
    pdb = loop.get_tag(["_Related_entries.Database_accession_code"])
print (pdb[0])

print("")
array = []
for loop in entry.get_loops_by_category("_Gen_dist_constraint") :
    array.append(loop.get_tag(['Atom_ID_1']))
    print("here")    
print(array);
#pdb =entry.get_loops_by_category("_Related_entries").get_tag(["_Related_entries.Database_accession_code"])
