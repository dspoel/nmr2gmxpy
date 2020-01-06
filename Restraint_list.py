import Restraint
import pynmrstar
import os
import numpy as np

class Restraint_list:
    def __init__(self, mr_file):
        self.restraints = [];
        
        entry = create_pynmrstar_entry(mr_file)
        DR_result_sets = self.create_data_array_from_pynmrstar_entry(entry)
        
        # Convert the array to numpy array
        DR_array = np.array(DR_result_sets)
        
        # 3d array
        # Checking if it has correct format!
        # If number of lines is 0 cause error
        if DR_array.shape == (0,): 
            print("**Format Error : Different NMR restraint format for PDB id : " , mr_file)
            # If it has different format then remove it 
            #os.remove(dist_res_file) 
#CATCH            #return None
        
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
