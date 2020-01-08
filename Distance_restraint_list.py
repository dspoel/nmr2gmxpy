import Restraint_list
import Distance_restraint

class Distance_restraint_list(Restraint_list.Restraint_list):

    def __init__(self, mr_file, verbose=False):
        Restraint_list.Restraint_list.__init__(self,mr_file, verbose)
        # 1 - for time and ensemble average and
        # 2 - for no time and ensemble average
        self.type_average = 1
    
    def create_data_array_from_pynmrstar_entry(self, entry):
        # print output if verbose
        super().create_data_array_from_pynmrstar_entry(entry)
        
        result_sets = []
        for loop in entry.get_loops_by_category("_Gen_dist_constraint") :
            result_sets.append(loop.get_tag(['ID','Auth_seq_ID_1' ,'Atom_ID_1','Comp_ID_1', 'Auth_seq_ID_2','Atom_ID_2' ,'Comp_ID_2','Distance_lower_bound_val','Distance_upper_bound_val'])) 
        
        return result_sets
    
    def init_list(self, data_array):
        # print output if verbose
        super().init_list(data_array)
        
        self.restraints = [];
        total = data_array.shape[0]
        for i in range(total):
            self.restraints.append(Distance_restraint.Distance_restraint(data_array[i,]))
        self.check()
    
    def set_type_average(self, type_in):
        type_average = type_in
        for element in self.restraints:
            element.set_type_average(type_in)

    def change_units(self):
        if self.verbose:
            print("Change units from angstrom to nanometers...")
        super().change_units()

    def check(self):
        if self.restraints[0].check_if_zero():
            raise Restraint_list.FormatError(
                "different residue number in NMR restraints file '%s' for PDB id"%self.mr_file)
                
        
        for element in self.restraints:
            if element.distance_upper_bound == '.' and element.distance_lower_bound == '.':
                raise Restraint_list.FormatError(
                    "No distance upper and lower bounds in NMR restraints file '%s' for PDB id"%self.mr_file)
            elif element.distance_upper_bound == '.':
                raise Restraint_list.FormatError(
                    "No distance upper bound in NMR restraints file '%s' for PDB id"%self.mr_file)
            elif element.distance_lower_bound == '.':
                raise Restraint_list.FormatError(
                    "No distance lower bound in NMR restraints file '%s' for PDB id"%self.mr_file)



