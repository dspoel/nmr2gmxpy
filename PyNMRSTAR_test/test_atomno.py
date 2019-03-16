import mdjoy
import mdjoy.top as top
import numpy as np

def get_file(filenm): 
    global atoms
    itp = top.read(filenm)
    atoms = [inst for inst in itp if isinstance(inst, top.GmxTopAtom)]    
    #print(dir(atoms[0]))

def get_atomno(res_nr,atom_nm,res_nm):
    #top_info = []
    atom_no = 0
    for atom in atoms:
        #print("Atom name :",atom_nm)
        #print("residue name : ",res_nm)
        #print("residue nr : ",res_nr)
        if atom.atom == atom_nm and  atom.residue == res_nm and atom.resnr == res_nr :
            atom_no =  atom.nr

    return atom_no
      



