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

from nmr2gmxpy_lib.Restraint import Restraint
from nmr2gmxpy_lib.AtomDefinition import AtomDefinition, NMRStarNelements
from nmr2gmxpy_lib.Atoms_names_amber import Atoms_names_amber

class Orientation_restraint (Restraint):
    def __init__(self,data):
        if len(data) < 10:
            return
        Restraint.__init__(self)
        self.id      = data[0]
        index   = 1
        nelem = NMRStarNelements()
        for i in range(2):
            self.atoms.append(AtomDefinition.fromList(data[index:index+nelem]))
            index += nelem
        
        self.RDC     = data[index]
        index += 1
        
        #value for force constant. Always 1?
        self.fac = 1.0
        
#    def replace_atoms_names_and_groups(self):
        # Replace atom names by using atoms names and residue names 
        # and assigns nuber of hydogens in the ME_group1 and ME_group2
        # for example, ME_group1 = 3 if methyl group, 2 if methylene group and 1 if methine group
#        self.atom1.atom_name, self.group_1 = Atoms_names_amber.atom_replace(self.atom1)
#        self.atom2.atom_name, self.group_2 = Atoms_names_amber.atom_replace(self.atom2)
        
    def write_header_in_file(self, fp):
        fp.write("[ orientation_restraints ]\n")
        fp.write(";    ai\t    aj\t  type\t  exp.\t label\t alpha\tconst.\t  obs.\tweight\n")
        fp.write(";      \t      \t      \t      \t      \t   Hz \t nm^3 \t   Hz \t Hz^-2\n\n")
    
    def write_data_in_file(self, fp, my_number):
        atom_no = []
        for i in range(2):
            self.atoms[i].setAtomId(Atoms_names_amber.get_atom_number(self.atoms[i]))
            atom_no.append(self.atoms[i].atom_id)
        if atom_no[0] and atom_no[1]:
            alpha = 3 #assign value for alpha
            const = 6.083 #assign value for constant
            weight = 1.0 # assign value for weight
            type_orientation = 1
            exp = 1
            fp.write("%6s\t%6s\t%6s\t%6s\t%6s\t%6s\t%6s\t%6s\t%6s\n" %
                    (atom_no[0], atom_no[1], type_orientation, exp, my_number+1,
                    alpha, const, self.RDC, weight))
        else:
            fp.write("; Could not find all atoms for orientation restraint %s %s\n" %
                    ( self.atoms[0].string(), self.atoms[1].string() ))

        




