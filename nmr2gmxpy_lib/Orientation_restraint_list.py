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

from nmr2gmxpy_lib.Atom_definition import NMRStarNames
from nmr2gmxpy_lib.Restraint_list import Restraint_list
from nmr2gmxpy_lib.Orientation_restraint import Orientation_restraint

class Orientation_restraint_list(Restraint_list):

    def create_data_array_from_pynmrstar_entry(self, entry):
        result_sets = []
        for loop in entry.get_loops_by_category("_RDC_constraint"):
            mylist = [ 'ID' ] + NMRStarNames(1) + NMRStarNames(2) + [ 'RDC_val' ]
            result_sets.append(loop.get_tag(mylist))
        
        return result_sets
    
    def init_list(self, data_array):
        if self.verbose:
            print("Initialize orientation restraints list of %i elements..." % data_array.shape[0])

        self.restraints = [];
        total = data_array.shape[0]
        for i in range(total):
            self.restraints.append(Orientation_restraint(data_array[i,]))
