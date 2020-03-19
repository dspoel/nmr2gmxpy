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
from pynmrstar import pynmrstar
import os
import numpy as np

# Exeptions which will be treated as warnings
class FormatError(Exception):
    def __init__(self, msg=None):
        pass
        

class Restraint_list:
    def __init__(self, mr_file, verbose=False):
        self.verbose = verbose
        self.restraints = []
        self.mr_file = mr_file
        entry = create_pynmrstar_entry(mr_file)
        DR_result_sets = self.create_data_array_from_pynmrstar_entry(entry)
        
        # Convert the array to numpy array
        DR_array = np.array(DR_result_sets)
        
        # 3d array
        # If number of lines is 0 cause error
        if DR_array.shape == (0,):
            raise FormatError("No information for the restraints in the file: '%s'"% mr_file)
        
        #take the first (and only one) element 
        DR_array_0 = np.array(DR_array[0,])
        self.init_list(DR_array_0);

    def set_verbose(self, verbose):
        self.verbose = verbose
        #for element in self.restraints:
        #    element.set_verbose(verbose)
            
    def get_verbose(self):
        return self.verbose

    def create_data_array_from_pynmrstar_entry(self, entry):
        # mast be defined in a child
        # return 3d array: number of molecules; number of atoms; number of arguments for atom (defined in restraint child)
        if self.verbose:
            print("Create entry from NMRstar file...")
        pass

    def init_list(self, data_array):
        # must be defined in a child
        if self.verbose:
            print("Initialize restraints list of %i elements..."%data_array.shape[0])
        pass
    
    def replace_atoms_names_and_groups(self):
        if self.verbose:
            print("Change atom names for GROMACS...")
        
        for element in self.restraints:
            element.replace_atoms_names_and_groups()
    
    def change_units(self):
    # only who needs this
        for element in self.restraints:
            element.change_units()
    
    def write_header_in_file(self, fp):
        self.restraints[0].write_header_in_file(fp);
        
    def write_data_in_file(self, itp_fp):
        if self.verbose:
            print("Writting .itp file...")
        for i, element in enumerate(self.restraints):
            element.write_data_in_file(itp_fp, i)
    
def create_pynmrstar_entry(mr_file):
    # Check if there is a restraint file in the PDB
    exists = os.path.isfile(mr_file)
    if exists:
        entry = pynmrstar.Entry.from_file(mr_file)
    else:
        print("**Error : No NMR restraint file on PDB")

    return entry
