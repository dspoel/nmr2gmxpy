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
    def init_atoms_list(cls, pdbfile_name):
        try:
            with open(pdbfile_name, "r") as inf:
                for line in inf:
                    if line.find("ATOM") == 0:
                        atomnm = line[12:16].strip()
                        # Some hacking required: if atomname starts with a number, we move it to the end.
                        if atomnm[0] in [ "1", "2", "3" ]:
                            atomnm = atomnm[1:] + atomnm[0]
                        atom = { "nr": int(line[6:11]),
                                 "atom": atomnm,
                                 "resnm": line[17:20].strip(),
                                 "chain_id": line[21:22].strip(),
                                 "resnr": int(line[23:26]) }
                        cls.atoms.append(atom)
            print("There are %d atoms in the translation table" % len(cls.atoms))
        except FileNotFoundError:
            print("Cannot open %s" % pdbfile_name)
            exit(1)

    # static function
    @classmethod
    def get_atom_number(cls, chain_id, res_nr, atom_name):
        atom_number = None
        for atom in cls.atoms:
            if ("atom" in atom and "resnr" in atom and "chain_id" in atom and "nr" in atom and
                (atom["atom"] == atom_name  and atom["resnr"] == res_nr)): # and atom["chain_id"] == chain_id)):
                atom_number = atom["nr"]
                break
        if not atom_number:
#            myatom = ("Chain %s Residue %d Name %s" % ( chain_id, res_nr, atom_name ))
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
