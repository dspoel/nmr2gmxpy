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
from nmr2gmxpy_lib.Atom_definition import Atom_definition, NMRStarNelements
from nmr2gmxpy_lib.Atom_names import Atom_names

class Distance_restraint (Restraint):
    def __init__(self,data):
        if len(data) < 9:
            return
        Restraint.__init__(self)
        self.id = data[0]
        index   = 1
        nelem = NMRStarNelements()
        for i in range(2):
            self.atoms.append(Atom_definition.fromList(data[index:index+nelem]))
            index += nelem
        
        self.distance_lower_bound = data[index]
        index += 1
        # if lower bound is not set in file then set to 0.0
        if (self.distance_lower_bound == '.'):
            self.distance_lower_bound = 0.0
        self.distance_upper_bound = data[index]
        index += 1
        # will be changed
        self.distance_upper_bound_2 = 0.0
        
        #value for force constant. Always !?
        self.fac = 1.0
        
        # 1 - for time and ensemble average and
        # 2 - for no time and ensemble average
        self.type_average = 1
        
    def set_type_average(self, value):
        self.type_average = value
        
    def change_units(self):
        # Change distances angstrom to nanometer
        self.distance_lower_bound = round(float(self.distance_lower_bound) * 0.10, 2)
        self.distance_upper_bound = round(float(self.distance_upper_bound) * 0.10, 2)
        self.distance_upper_bound_2 = round(float(self.distance_upper_bound) + 0.1, 2)
    
    def write_header_in_file(self, fp):
        fp.write("[ distance_restraints ]\n")
        fp.write(";    ai\t    aj\t  type\t index\t type'\t   low\t   up1\t   up2\t   fac\n\n")

    def write_data_in_file(self, fp, my_number):
        orig_atoms = []
        for i in range(len(self.atoms)):
            orig_atoms.append(self.atoms[i].atom_name)

        for p in range(self.atoms[0].group):
            if self.atoms[0].group > 1:
                self.atoms[0].setName(orig_atoms[0] + str(p+1))
            for q in range(self.atoms[1].group):
                if self.atoms[1].group > 1:
                    self.atoms[1].setName(orig_atoms[1] + str(q+1))
                # For residue number and atom name(orig_atom1,orig_atom2)
                # find atom number from 2lv8.top and assign it to ai(atom_no1) and aj(atom_no2)
                for i in range(2):
                    self.atoms[i].setAtomId(Atom_names.get_atom_number(self.atoms[i]))
                atom_no1 = self.atoms[0].atomId()
                atom_no2 = self.atoms[1].atomId()
                if atom_no1 and atom_no2:
                    fp.write("%6s\t%6s\t     1\t%6d\t%6d\t%6s\t%6s\t%6s\t%6s\n"%
                            (atom_no1, atom_no2, int(self.id),
                            self.type_average, 
                            self.distance_lower_bound, 
                            self.distance_upper_bound,
                            self.distance_upper_bound_2,
                            self.fac))
                else:
                    fp.write("; Could not find all atoms for distance restraint %s %s\n" %
                         ( self.atoms[0].string(), self.atoms[1].string() ))
            for i in range(len(self.atoms)):
                self.atoms[i].setName(orig_atoms[i])

