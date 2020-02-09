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

import pynmrstar
import os
import numpy as np

class Restraint():
    """
    # Abstract parent class for all restraints
    """
    def __init__(self, data_array):
        self.verbose = False
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
        # should be implemented in a child
        pass
    
    def change_units(self):
        # if is needed should be implemented in a child
        pass
    

