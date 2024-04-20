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
from nmr2gmxpy_lib.Dihedral_restraint import Dihedral_restraint

class Dihedral_restraint_list(Restraint_list):

    def create_data_array_from_pynmrstar_entry(self, entry):
        # print output if verbose
        super().create_data_array_from_pynmrstar_entry(entry)
        
        result_sets = []
        mylist = [ 'ID' ] + NMRStarNames(1) + NMRStarNames(2) + NMRStarNames(3) + NMRStarNames(4) + [ 'Angle_lower_bound_val', 'Angle_upper_bound_val' ]

        loops = entry.get_loops_by_category("_Torsion_angle_constraint")
        if self.verbose and len(loops) > 1:
            print("There are %d dihres loops" % len(loops))
        newtags = []
        for loop in loops[:1]:
            for tag in loop.get_tag(mylist):
                # Only add this entry if we found everything we need
                if len(tag) == len(mylist):
                    newtags.append(tag)
        result_sets.append(newtags)

        return result_sets
    
    def init_list(self, data_array):
        # print output if verbose
        super().init_list(data_array)

        self.restraints = [];
        total = data_array.shape[0]
        for i in range(total):
            self.restraints.append(Dihedral_restraint(data_array[i,]))
