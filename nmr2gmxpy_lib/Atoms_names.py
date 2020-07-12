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


# parent abstract(!) class for every concrete force field atoms names
# in every child of this class define the name in 'force_filed' and the
# function 'atom_replace', where you replace atoms nmr names tp force filed
# atom names.

import mdjoy
import mdjoy.top as top
import numpy as np
from random import randint

class AtomsNamesError(Exception):
    def __init__(self, msg=None):
        pass


# static class
class Atoms_names():
    # static
    atoms = []
    
    
    # static function
    @classmethod
    def init_atoms_list(cls, topfile_name):
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
            if atom.atom == atom_name  and atom.resnr == res_nr:
                atom_number =  atom.nr
        if atom_number==0:
            raise AtomsNamesError("""
Names of atom in the NMRstar file does not coincide with any name of an atom
in the topology file. Make sure that you use the correct force field.
Do not forget to use -ignh flag when you generate the .top file with the
pdb2gmx program. This forces GROMACS to remove and recreate hydrogen atoms.
In some cases this can lead to problems though, for instance if GROMACS cannot
guess the correct protonatation. In that case assign the side chain protonation
state manually.

Problem: cannot find in topology file the name for residue %d atom %s.""" % ( res_nr, atom_name ) )
        return atom_number
    
    # static method
    @classmethod 
    def atom_replace(cls, atom_nm,res_nm):
        # define in child
        pass
