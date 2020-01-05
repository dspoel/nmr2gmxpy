import Restraint

class Distance_restraint (Restraint.Restraint):
    def __init__(self,data_array):
    # No call of parent constructor
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

        self.distance_lower_boundary_value = data_array[7]
        self.distance_upper_boundary_value = data_array[8]
        
    #def print_all(self):
    #    print(self.id, self.atom_id_1, self.comp_id_1, self.atom_id_2, self.comp_id_2,
    #            self.distance_lower_boundary_value, self.distance_upper_boundary_value)
    
