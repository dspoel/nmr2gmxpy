import pynmrstar
import os
import numpy as np

class Restraint():
    def __init__(self, data_array):
#        self.id = 0
#        self.atom_id1 = ""
#        self.atom_id2 = ""
#        self.comp_id1 = ""
#        self.comp_id2 = ""
#        self.distance_lower_boundary_value = 0
#        self.distance_upper_boundary_value = 0

#    def init(self, data_array):
        self.id = data_array[0]
        self.atom_id_1 = data_array[2]
        self.atom_id_2 = data_array[5]

        self.comp_id_1 = data_array[3]
        self.comp_id_2 = data_array[6]

        self.distance_lower_boundary_value = data_array[7]
        self.distance_upper_boundary_value = data_array[8]

    
    def print_all(self):
        print(self.id, self.atom_id_1, self.comp_id_1, self.atom_id_2, self.comp_id_2,
                self.distance_lower_boundary_value, self.distance_upper_boundary_value)

def init_with_NMR_file(mr_file):
    # Patch the parser
    from monkeypatch import patch_parser, unpatch_parser
    patch_parser(pynmrstar)

    # Check if there is a restraint file in the PDB
    exists = os.path.isfile(mr_file)
    if exists:
        entry = pynmrstar.Entry.from_file(mr_file)
    else:
        print("**Error : No NMR restraint file on PDB")
#CATCH            #return None

    # Get Distance Restraints from the file and
    # store them into DR_result_sets
    DR_result_sets = []
    for distance_restraints_loop in entry.get_loops_by_category("_Gen_dist_constraint") :
        DR_result_sets.append(distance_restraints_loop.get_tag(['ID','Auth_seq_ID_1' ,'Atom_ID_1','Comp_ID_1', 'Auth_seq_ID_2','Atom_ID_2' ,'Comp_ID_2','Distance_lower_bound_val','Distance_upper_bound_val'])) 

    # Restore the original parser .. recall we patched the parser before.
    unpatch_parser(pynmrstar)
    # Convert the array to numpy array
    DR_array = np.array( DR_result_sets)
    
    # Checking if it has correct format!
    # If number of lines is 0 cause error
    if DR_array.shape == (0,): 
        print("**Format Error : Different NMR restraint format for PDB id : " , file_nm)
            # If it has different format then remove it 
            #os.remove(dist_res_file) 
#CATCH            #return None
    DR_array_0 = np.array(DR_array[0,])
    total = DR_array_0.shape[0]
    restraints = []
    for i in range(total):
        restraints.append(Restraint(DR_array_0[i,]))

    
    return restraints

