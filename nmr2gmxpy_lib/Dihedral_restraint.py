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

class Dihedral_restraint (Restraint):
    def __init__(self,data):
        if len(data) < 15:
            return
        Restraint.__init__(self)
        self.id      = data[0]
        index   = 1
        nelem = NMRStarNelements()
        for i in range(4):
            self.atoms.append(AtomDefinition.fromList(data[index:index+nelem]))
            index += nelem
        
        self.angle_lower_boundary = float(data[index])
        index += 1
        self.angle_upper_boundary = float(data[index])
        index += 1
        
        self.fac = 1000.0
        
#    def replace_atoms_names_and_groups(self):
        #replacing atom names by using atoms names and residue names 
        #and assigns nuber of hydogens in the ME_group1 and ME_group2
        #for example, ME_group1 = 3 if methyle group, 2 if methylene group and 1 if methine group 
        # for more info see test_atomno.py
#        self.atom1.atom_name, self.group_1 = Atoms_names_amber.atom_replace(self.atom1)
#        self.atom2.atom_name, self.group_2 = Atoms_names_amber.atom_replace(self.atom2)
#        self.atom3.atom_name, self.group_3 = Atoms_names_amber.atom_replace(self.atom3)
#        self.atom4.atom_name, self.group_4 = Atoms_names_amber.atom_replace(self.atom4)
        
    def write_header_in_file(self, fp):
        fp.write("[ dihedral_restraints ]\n")
        fp.write(";    ai\t    aj\t    ak\t    al\t  type\t   phi\t  dphi\t   fac\n\n")
        
    def write_data_in_file(self, fp, my_number):
        # g1,g2,g3 and g4 extra output from the fucntion atom_replace in module test_atomno.py
        # getting atom number from residue number and atom name
        atom_no = []
        for i in range(len(self.atoms)):
            self.atoms[i].setAtomId(Atoms_names_amber.get_atom_number(self.atoms[i]))
            atom_no.append(self.atoms[i].atom_id)
        if atom_no[0] and atom_no[1] and atom_no[2] and atom_no[3]:
            phi = round(( self.angle_upper_boundary + self.angle_lower_boundary)/2.0, 2)
            dphi = round((self.angle_upper_boundary - self.angle_lower_boundary)/2.0, 2)
            fac = 1.0 # assign value for force constant
            fp.write("%6s\t%6s\t%6s\t%6s\t     1\t%6s\t%6s\t%6s\n" % (atom_no[0], atom_no[1],
                                                                      atom_no[2],atom_no[3],
                                                                      phi,dphi,self.fac))
        else:
            fp.write("; Could not find all atoms for dihedral restraint %s %s %s %s\n" %
                         ( self.atoms[0].string(), self.atoms[1].string(),
                           self.atoms[2].string(), self.atoms[3].string()))





