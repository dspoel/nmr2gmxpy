import Restraint_list
import Dihedral_restraint

class Dihedral_restraint_list(Restraint_list.Restraint_list):

    def __init__(self, mr_file, verbose=False):
        Restraint_list.Restraint_list.__init__(self, mr_file, verbose)
        # 1 - for time and ensemble average and
        # 2 - for no time and ensemble average
        self.type_average = 1
    
    def create_data_array_from_pynmrstar_entry(self, entry):
        # print output if verbose
        super().create_data_array_from_pynmrstar_entry(entry)
        
        result_sets = []
        for loop in entry.get_loops_by_category("_Torsion_angle_constraint") :
            result_sets.append(loop.get_tag(['ID',
                            'PDB_residue_no_1', 'Comp_ID_1', 'Atom_ID_1',
                            'PDB_residue_no_2', 'Comp_ID_2','Atom_ID_2',
                            'PDB_residue_no_3', 'Comp_ID_3', 'Atom_ID_3',
                            'PDB_residue_no_4', 'Comp_ID_4', 'Atom_ID_4', 
                            'Angle_lower_bound_val','Angle_upper_bound_val']))

        return result_sets
    
    def init_list(self, data_array):
        # print output if verbose
        super().init_list(data_array)

        self.restraints = [];
        total = data_array.shape[0]
        for i in range(total):
            self.restraints.append(Dihedral_restraint.Dihedral_restraint(data_array[i,]))