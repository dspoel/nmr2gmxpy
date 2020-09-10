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
For some residues in NMR file, change the atom names to the Amber FF.
"""

from nmr2gmxpy_lib.Atoms_names import Atoms_names
from nmr2gmxpy_lib.AtomDefinition import AtomDefinition

class Atoms_names_amber(Atoms_names):
    force_field = "AMBER"
    
    # static method
    @classmethod 
    def atom_replace(cls, atom_def):
        ME_group = 1

        atom_nm = atom_def.atom_name
        res_nm  = atom_def.res_name
        res_nr  = atom_def.res_id
        # N-terminal H: needs debugging.
        if res_nr == 1 and atom_nm == 'H' and False:
            if res_nm == 'PRO':
                ME_group = 2
            else:
                ME_group = 3
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
#checked
        if res_nm == 'TRP':
            if atom_nm == 'HB2':
                atom_nm = 'HB1'
            if atom_nm == 'HB3':
                atom_nm = 'HB2'

#checked
        if res_nm == "HIS": # change name to 'HID' like in amber.ff !
            if atom_nm == 'HB2':
                atom_nm = 'HB1'
            if atom_nm == 'HB3':
                atom_nm = 'HB2'
#        if res_nm == 'HIS':
#            if atom_nm == 'HB2':
#                atom_nm = 'HB1'
#            if atom_nm == 'HB3':
#                atom_nm = 'HB2'
#            if atom_nm == 'HE2':
#                atom_nm = 'HE1'
#            if atom_nm == 'HE3':
#                atom_nm = 'HE2'
# SHOULD BE OTHER WAY AROUND?
#            if atom_nm == 'HD1':
#                atom_nm = 'HD2'

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
    
#checked
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

#checked
        if res_nm == 'VAL':
            if atom_nm == 'MG2':
                atom_nm = 'HG2'
                ME_group = 3
            if atom_nm == 'MG1':
                atom_nm = 'HG1'
                ME_group = 3

#checked
        if res_nm == 'ALA':
            if atom_nm == 'MB':
                atom_nm = 'HB' 
                ME_group = 3
#checked
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
#DNA/RNA, checked
        if res_nm == 'G' or res_nm == "A" or res_nm == "U" or res_nm == "C" or res_nm == 'DG' or res_nm == "DA" or res_nm == "DT" or res_nm == "DC":
            if atom_nm == "HO2'":
                atom_nm = "HO'2"
            elif atom_nm == "H5'":
                atom_nm = "H5'1"
            elif atom_nm == "H5''":
                atom_nm = "H5'2"
            elif atom_nm == "H2'":
                atom_nm = "H2'1"
            elif atom_nm == "H2''":
                atom_nm = "H2'2"
            elif atom_nm == "M7" and res_nm == "DT":
                atom_nm = "H7"
                ME_group = 3
    
        return atom_nm,ME_group

