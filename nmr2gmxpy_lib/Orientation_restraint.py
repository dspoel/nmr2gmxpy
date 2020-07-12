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
from nmr2gmxpy_lib.Atoms_names_amber import Atoms_names_amber

class Orientation_restraint (Restraint):
    def __init__(self,data_array):
        if len(data_array) < 10:
            return
        Restraint.__init__(self, data_array)
        self.id = data_array[0]

        if data_array[1] != ".":
            self.residue_1 = int(data_array[1])
        else:
            self.residue_1 = int(data_array[4])
        self.comp_id_1 = data_array[2]
        self.atom_id_1 = data_array[3]
        self.seq_id_1  = data_array[4]
        
<<<<<<< HEAD
        self.residue_2 = int(data_array[5])
        self.comp_id_2 = data_array[6]
        self.atom_id_2 = data_array[7]
        self.seq_id_2  = data_array[8]
=======
        if data_array[5] != ".":
            self.residue_2 = int(data_array[5])
        else:
            self.residue_2 = int(data_array[8])
        self.comp_id_2 = data_array[6]
        self.atom_id_2 = data_array[7]
>>>>>>> master
        
        self.RDC = data_array[9]
        
        self.group_1 = 0
        self.group_2 = 0
        
        #value for force constant. Always 1?
        self.fac = 1.0
        
    def replace_atoms_names_and_groups(self):
        #replacing atom names by using atoms names and residue names 
        #and assigns nuber of hydogens in the ME_group1 and ME_group2
        #for example, ME_group1 = 3 if methyle group, 2 if methylene group and 1 if methine group 
        # for more info see test_atomno.py
        self.atom_id_1, self.group_1 = Atoms_names_amber.atom_replace(self.atom_id_1, self.comp_id_1, self.residue_1)
        self.atom_id_2, self.group_2 = Atoms_names_amber.atom_replace(self.atom_id_2, self.comp_id_2, self.residue_1)
        
    def write_header_in_file(self, fp):
        fp.write("[ orientation_restraints ]\n")
        fp.write(";    ai\t    aj\t  type\t  exp.\t label\t alpha\tconst.\t  obs.\tweight\n")
        fp.write(";      \t      \t      \t      \t      \t   Hz \t nm^3 \t   Hz \t Hz^-2\n\n")
    
    def write_data_in_file(self, fp, my_number):
        atom_1 = Atoms_names_amber.get_atom_number(self.seq_id_1, self.residue_1, self.atom_id_1)
        atom_2 = Atoms_names_amber.get_atom_number(self.seq_id_2, self.residue_2, self.atom_id_2)
        alpha = 3 #assign value for alpha
        const = 6.083 #assign value for constant
        weight = 1.0 # assign value for weight
        type_orientation = 1
        exp = 1
        fp.write("%6s\t%6s\t%6s\t%6s\t%6s\t%6s\t%6s\t%6s\t%6s\n" %
                (atom_1, atom_2, type_orientation, exp, my_number+1,
                alpha, const, self.RDC, weight))
        




