import Restraint
import pynmrstar
import os
import numpy as np

class FormatError(Exception):
    def __init__(self, msg=None):
        pass
        

class Restraint_list:
    def __init__(self, mr_file):
        self.restraints = []
        self.mr_file = mr_file
        entry = create_pynmrstar_entry(mr_file)
        DR_result_sets = self.create_data_array_from_pynmrstar_entry(entry)
        
        # Convert the array to numpy array
        DR_array = np.array(DR_result_sets)
        
        # 3d array
        # If number of lines is 0 cause error
        if DR_array.shape == (0,):
            raise FormatError("Different NMR restraint format for PDB id in file: %s"% mr_file)
        
        #take the first (and only one) element 
        DR_array_0 = np.array(DR_array[0,])
        self.init_list(DR_array_0);



    def create_data_array_from_pynmrstar_entry(self, entry):
        # mast be defined in a child
        # return 3d array: number of molecules; number of atoms; number of arguments for atom (defined in restraint child)
        pass

    def init_list(self, data_array_2d):
        # must be defined in a child
        pass
    
    def replace_atoms_names_and_groups(self):
        for element in self.restraints:
            element.replace_atoms_names_and_groups()
    
    def check_this_object(self):
    #TO DO!
        pass
    
    def change_units(self):
    # only who needs this
        for element in self.restraints:
            element.change_units()
    
    def write_header_in_file(self, fp):
        self.restraints[0].write_header_in_file(fp);
        
    def write_data_in_file(self, itr_fp):
        for i, element in enumerate(self.restraints):
            element.write_data_in_file(itr_fp, i)
    
def create_pynmrstar_entry(mr_file):
    # Patch the parser
    from monkeypatch import patch_parser, unpatch_parser
    patch_parser(pynmrstar)

    # Check if there is a restraint file in the PDB
    exists = os.path.isfile(mr_file)
    if exists:
        entry = pynmrstar.Entry.from_file(mr_file)
    else:
        print("**Error : No NMR restraint file on PDB")
#CATCH   #return None

    # Restore the original parser .. recall we patched the parser before.
    unpatch_parser(pynmrstar)
    return entry
