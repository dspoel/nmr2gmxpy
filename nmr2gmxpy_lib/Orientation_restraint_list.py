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

from nmr2gmxpy_lib.Restraint_list import Restraint_list
from nmr2gmxpy_lib.Orientation_restraint import Orientation_restraint

class Orientation_restraint_list(Restraint_list):

    def __init__(self, mr_file, verbose=False):
        Restraint_list.__init__(self, mr_file, verbose)
        # 1 - for time and ensemble average and
        # 2 - for no time and ensemble average
        self.type_average = 1
    
    def create_data_array_from_pynmrstar_entry(self, entry):
        # print output if verbose
        super().create_data_array_from_pynmrstar_entry(entry)
        
        result_sets = []
        for loop in entry.get_loops_by_category("_RDC_constraint") :
            result_sets.append(loop.get_tag(['ID',
                            'PDB_residue_no_1', 'Comp_ID_1', 'Atom_ID_1', 'PDB_strand_ID_1',
                            'PDB_residue_no_2', 'Comp_ID_2', 'Atom_ID_2', 'PDB_strand_ID_2',
                            'RDC_val']))
        
        return result_sets
        
    
    def init_list(self, data_array):
        # print output if verbose
        super().init_list(data_array)

        self.restraints = [];
        total = data_array.shape[0]
        for i in range(total):
            self.restraints.append(Orientation_restraint(data_array[i,]))
