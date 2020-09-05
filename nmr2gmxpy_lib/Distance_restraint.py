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

class Distance_restraint (Restraint):
    def __init__(self,data_array):
        if len(data_array) < 9:
            return
        Restraint.__init__(self, data_array)
        self.id = data_array[0]
        self.atom_id_1 = data_array[3]
        self.atom_id_2 = data_array[7]

        self.comp_id_1 = data_array[2]
        self.comp_id_2 = data_array[6]
        
        self.seq_id_1 = int(data_array[1])
        self.seq_id_2 = int(data_array[5])

        self.chain_id_1 = data_array[4]
        self.chain_id_2 = data_array[8]
        # will be changed
        self.group_1 = 0
        self.group_2 = 0
        
        self.distance_lower_bound = data_array[9]
        # if lower bound is not set in file then set to 0.0
        if(data_array[9]=='.'):
            self.distance_lower_bound = 0.0
        self.distance_upper_bound = data_array[10]
        # will be changed
        self.distance_upper_bound_2 = 0.0
        
        #value for force constant. Always !?
        self.fac = 1.0
        
        # 1 - for time and ensemble average and
        # 2 - for no time and ensemble average
        self.type_average = 1
        
    def set_type_average(self, value):
        self.type_average = value
        
    def replace_atoms_names_and_groups(self):
        #replacing atom names by using atoms names and residue names 
        #and assigns nuber of hydogens in the ME_group1 and ME_group2
        #for example, ME_group1 = 3 if methyle group, 2 if methylene group and 1 if methine group 
        # for more info see test_atomno.py
        self.atom_id_1, self.group_1 = Atoms_names_amber.atom_replace(self.atom_id_1, self.comp_id_1, self.seq_id_1)
        self.atom_id_2, self.group_2 = Atoms_names_amber.atom_replace(self.atom_id_2, self.comp_id_2, self.seq_id_1)
        pass
    
    def change_units(self):
    # Change distances angstrom to nanometer
        self.distance_lower_bound = round(float(self.distance_lower_bound) * 0.10, 2)
        
        self.distance_upper_bound = round(float(self.distance_upper_bound) * 0.10, 2)
        self.distance_upper_bound_2 = round(float(self.distance_upper_bound) + 0.1, 2)
    
    def write_header_in_file(self, fp):
        fp.write("[ distance_restraints ]\n")
        fp.write(";    ai\t    aj\t  type\t index\t type'\t   low\t   up1\t   up2\t   fac\n\n")

    def write_data_in_file(self, fp, my_number):
        for p in range(self.group_1):
            for q in range(self.group_2):
                current_atom1 = self.atom_id_1
                current_atom2 = self.atom_id_2
                if self.group_1 == 3 or self.group_1 == 2:
                    current_atom1 = current_atom1 + str(p+1)
                if self.group_2 == 3 or self.group_2 == 2:
                    current_atom2 = current_atom2 + str(q+1)
                
                # For residue number and atom name(current_atom1,current_atom2)
                # find atom number from 2lv8.top 
                # and assign it to ai(atom_no1) and aj(atom_no2)
                atom_no1 = Atoms_names_amber.get_atom_number(self.chain_id_1, self.seq_id_1, current_atom1)
                atom_no2 = Atoms_names_amber.get_atom_number(self.chain_id_2, self.seq_id_2, current_atom2)
                if atom_no1 and atom_no2:
                    fp.write("%6s\t%6s\t     1\t%6d\t%6d\t%6s\t%6s\t%6s\t%6s\n"%
                            (atom_no1, atom_no2, int(self.id),
                            self.type_average, 
                            self.distance_lower_bound, 
                            self.distance_upper_bound,
                            self.distance_upper_bound_2,
                            self.fac))
