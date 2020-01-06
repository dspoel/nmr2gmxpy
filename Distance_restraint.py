import Restraint
import test_atomno

class Distance_restraint (Restraint.Restraint):
    def __init__(self,data_array):
#        self.id = 0
#        self.atom_id1 = ""
#        self.atom_id2 = ""
#        self.comp_id1 = ""
#        self.comp_id2 = ""
#        self.distance_lower_boundary_value = 0
#        self.distance_upper_boundary_value = 0

#    def init(self, data_array):
        Restraint.Restraint.__init__(self, data_array)
        self.id = data_array[0]
        self.atom_id_1 = data_array[2]
        self.atom_id_2 = data_array[5]

        self.comp_id_1 = data_array[3]
        self.comp_id_2 = data_array[6]
        
        # assign this later
        self.group_1 = 0
        self.group_2 = 0

        self.distance_lower_boundary_value = float(data_array[7])
        self.distance_upper_boundary_value = float(data_array[8])
        
    #def print_all(self):
    #    print(self.id, self.atom_id_1, self.comp_id_1, self.atom_id_2, self.comp_id_2,
    #            self.distance_lower_boundary_value, self.distance_upper_boundary_value)
    
    def replace_atoms_names_and_groups(self):
        #replacing atom names by using atoms names and residue names 
        #and assigns nuber of hydogens in the ME_group1 and ME_group2
        #for example, ME_group1 = 3 if methyle group, 2 if methylene group and 1 if methine group 
        # for more info see test_atomno.py
        self.atom_id_1, self.group_1 = test_atomno.atom_replace(self.atom_id_1, self.comp_id_1)
        self.atom_id_2, self.group_2 = test_atomno.atom_replace(self.atom_id_2, self.comp_id_2)
    