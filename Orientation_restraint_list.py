import Restraint_list
import Orientation_restraint

class Orientation_restraint_list(Restraint_list.Restraint_list):

    def __init__(self, mr_file):
        Restraint_list.Restraint_list.__init__(self,mr_file)
        # 1 - for time and ensemble average and
        # 2 - for no time and ensemble average
        self.type_average = 1
    
    def create_data_array_from_pynmrstar_entry(self, entry):
        result_sets = []
        for loop in entry.get_loops_by_category("_RDC_constraint") :
            result_sets.append(loop.get_tag(['ID',
                            'PDB_residue_no_1', 'Comp_ID_1', 'Atom_ID_1',
                            'PDB_residue_no_2', 'Comp_ID_2', 'Atom_ID_2',
                            'RDC_val']))

        return result_sets
    
    def init_list(self, data_array_2d):
        self.restraints = [];
        total = data_array_2d.shape[0]
        for i in range(total):
            self.restraints.append(Orientation_restraint.Orientation_restraint(data_array_2d[i,]))
