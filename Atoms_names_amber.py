"""
For some residues in NMR filec change arom number to number-1 for gromacs
except ~line 89
"""

import mdjoy
import mdjoy.top as top
import numpy as np
from random import randint

class AtomsNamesError(Exception):
    def __init__(self, msg=None):
        pass


# static class
# TODO: make it abstract and implement other force fields as children of this one
class Atoms_names_amber():
    # static
    atoms = []
    
    # static function
    @classmethod
    def init_atoms_list(cls, topfile_name):
        #atomsaa = [inst for inst in topfile if isinstance(inst, top.GmxTopAtom)]
        topfile = top.read(topfile_name)
        for inst in topfile:
            if isinstance(inst, top.GmxTopAtom):
                cls.atoms.append(inst)
    
    # statuc function
    @classmethod
    def get_atom_number(cls, res_nr, atom_name):
        #top_info = []
        atom_number = 0

        for atom in cls.atoms:
            #if atom_nm==5:
            #print("Atom name :",atom_name)
                #print("residue name : ",res_nm)
                #print("residue nr : ",res_nr)
            if atom.atom == atom_name  and atom.resnr == res_nr:
                atom_number =  atom.nr
            #else:
                #print('[%s \t %s]' %(atom_nm,atom.atom))
        if atom_number==0:
            raise AtomsNamesError("Names of atoms in the NMRstar file does not coincide with names of atom in \
the topology file. The topology file can be generated only with AMBER force field.\
Also do not forget to use -ignh flag when you generate the .top file \
with pdb2gmx program. This forces GROMAX to rename hydrogen atoms.")
        return atom_number
    
    # static method
    @classmethod 
    def atom_replace(cls, atom_nm,res_nm):
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
# SHOULD BE OTHER WAY AROUND?
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

#checked
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
        
            if atom_nm == 'CD1':
                atom_nm = 'CD'
            if atom_nm == 'HD11':
                atom_nm = 'HD1'
            if atom_nm == 'HD12':
                atom_nm = 'HD2'
            if atom_nm == 'HD13':
                atom_nm = 'HD3'
        
#checked
        if res_nm == 'GLY':
            if atom_nm == 'HA2':
                atom_nm = 'HA1'
            if atom_nm == 'HA3':
                atom_nm = 'HA2'

    
        return atom_nm,ME_group

