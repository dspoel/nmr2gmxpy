import mdjoy
import mdjoy.top as top
import numpy as np
from random import randint

def get_file(filenm): 
    global atoms
    
    itp = top.read(filenm)
    atoms = [inst for inst in itp if isinstance(inst, top.GmxTopAtom)]    
    #print(dir(atoms[0]))

def get_atomno(res_nr,atom_nm):
    #top_info = []
    atom_no = 0
    for atom in atoms:
        #print("Atom name :",atom_nm)
        #print("residue name : ",res_nm)
        #print("residue nr : ",res_nr)
        if atom.atom == atom_nm  and atom.resnr == res_nr :
            atom_no =  atom.nr
        #else:
            #print('[%s \t %s]' %(atom_nm,atom.atom))

    return atom_no

def atom_replace(atom_nm,res_nm):
    ME_group = 1

    if res_nm == 'MET':
        if atom_nm == 'ME':
            atom_nm = 'HE' 
            ME_group = 3
        if atom_nm == 'HB2':
            atom_nm = 'HB1'
        if atom_nm == 'HB3':
            atom_nm = 'HB2' 
        if atom_nm == 'HG2':
            atom_nm = 'HG1'
        if atom_nm == 'HG3':
            atom_nm = 'HG2'

    if res_nm == 'LYS' or res_nm == 'ASN' or res_nm == 'SER' or res_nm == 'ASP' or res_nm == 'GLU' or res_nm == 'PRO' or res_nm == 'GLN' or res_nm == 'ARG'  or res_nm == 'CYS':
        if atom_nm == 'HB2':
            atom_nm = 'HB1'
        if atom_nm == 'HB3':
            atom_nm = 'HB2'
        if atom_nm == 'HD2':
            atom_nm = 'HD1'
        if atom_nm == 'HD3':
            atom_nm = 'HD2'
        if atom_nm == 'HE2':
            atom_nm = 'HE1'
        if atom_nm == 'HE3':
            atom_nm = 'HE2'
        if atom_nm == 'HG2':
            atom_nm = 'HG1'
        if atom_nm == 'HG3':
            atom_nm = 'HG2'      

    if res_nm == 'LYS':
        if atom_nm == 'QZ':
            atom_nm = 'HZ'
            ME_group = 3
        
    if res_nm == 'TRP':
        if atom_nm == 'HB2':
            atom_nm = 'HB1'
        if atom_nm == 'HB3':
            atom_nm = 'HB2'



    if res_nm == 'HIS':
        if atom_nm == 'HB2':
            atom_nm = 'HB1'
        if atom_nm == 'HB3':
            atom_nm = 'HB2'
        if atom_nm == 'HE2':
            atom_nm = 'HE1'
        if atom_nm == 'HE3':
            atom_nm = 'HE2'
        if atom_nm == 'HD1':
            atom_nm = 'HD2'


    if res_nm == 'ARG':
        if atom_nm == 'QH1':
            atom_nm = 'HH1'
            ME_group = 2
        if atom_nm == 'QH2':
            atom_nm = 'HH2'
            ME_group = 2     

    if res_nm == 'LEU':
        if atom_nm == 'MD2':
            atom_nm = 'HD2'
            ME_group = 3
        if atom_nm == 'MD1':
            atom_nm = 'HD1' 
            ME_group = 3
        if atom_nm == 'HB2':
            atom_nm = 'HB1'
        if atom_nm == 'HB3':
            atom_nm = 'HB2'
    

    if res_nm == 'TYR' or res_nm == 'PHE':
        if atom_nm == 'HB2':
            atom_nm = 'HB1'
        if atom_nm == 'HB3':
            atom_nm = 'HB2'
        if atom_nm == 'QD':
            atom_nm = 'HD'
            ME_group = 2
        if atom_nm == 'QE':
            atom_nm = 'HE'
            ME_group = 2


    if res_nm == 'VAL':
        if atom_nm == 'MG2':
            atom_nm = 'HG2'
            ME_group = 3
        if atom_nm == 'MG1':
            atom_nm = 'HG1'
            ME_group = 3


    if res_nm == 'ALA':
        if atom_nm == 'MB':
            atom_nm = 'HB' 
            ME_group = 3

    if res_nm == 'THR':
        if atom_nm == 'MG':
            atom_nm = 'HG2'
            ME_group = 3


    if res_nm == 'ILE':
        if atom_nm == 'MG':
            atom_nm = 'HG2'
            ME_group = 3
        if atom_nm == 'MD':
            atom_nm = 'HD'
            ME_group = 3
        if atom_nm == 'HG12':
            atom_nm = 'HG11'
        if atom_nm == 'HG13':
            atom_nm = 'HG12'

    if res_nm == 'GLY':
        if atom_nm == 'HA2':
            atom_nm = 'HA1'
        if atom_nm == 'HA3':
            atom_nm = 'HA2'

    
    return atom_nm,ME_group

