import pynmrstar
import test_atomno
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
    

