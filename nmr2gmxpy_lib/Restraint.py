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

import pynmrstar, os
from nmr2gmxpy_lib.Atoms_names_amber import Atoms_names_amber

class Restraint():
    """
    # Abstract parent class for all restraints
    """
    def __init__(self):
        self.verbose = False
        self.atoms   = []
        # Every child should define their own constructor

    def set_verbose(self,verbose):
        self.verbose = verbose

    def get_verbose(self):
        return self.verbose
    
    def print_all(self):
        #members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        #print (members)
        print("{")
        for attr in dir(self):
            if (not callable(getattr(self,attr)) and not attr.startswith("__")):
            
                print(attr + " = " + str(getattr(self, attr)))
                #print (getattr(self, attr))
            
        print("}")
    
    def replace_atoms_names_and_groups(self):
        # Replace atom names by using atoms names and residue names 
        # and assigns nuber of hydogens in the ME_group1 and ME_group2
        # for example, ME_group1 = 3 if methyl group, 2 if methylene group and 1 if methine group
        for i in range(len(self.atoms)):
            aname, group = Atoms_names_amber.atom_replace(self.atoms[i])
            self.atoms[i].setName(aname)
            self.atoms[i].setGroup(group)
#            self.atoms[i].setAtomId(Atoms_names_amber.get_atom_number(self.atoms[i]))
    
    def change_units(self):
        # if is needed should be implemented in a child
        pass
    

