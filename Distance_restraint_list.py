import Restraint_list
import Distance_restraint

class Distance_restraint_list(Restraint_list.Restraint_list):

    def __init__(self, mr_file):
        Restraint_list.Restraint_list.__init__(self,mr_file)
        #create_data_array_2d_from_pynmrstar_entry(self, entry):
        
    
    def create_data_array_2d_from_pynmrstar_entry(self, entry):
        DR_result_sets = []
        for distance_restraints_loop in entry.get_loops_by_category("_Gen_dist_constraint") :
            DR_result_sets.append(distance_restraints_loop.get_tag(['ID','Auth_seq_ID_1' ,'Atom_ID_1','Comp_ID_1', 'Auth_seq_ID_2','Atom_ID_2' ,'Comp_ID_2','Distance_lower_bound_val','Distance_upper_bound_val'])) 
        return DR_result_sets
    
    def init_list(self, data_array_2d):
        self.restraints = [];
        total = data_array_2d.shape[0]
        for i in range(total):
            self.restraints.append(Distance_restraint.Distance_restraint(data_array_2d[i,]))