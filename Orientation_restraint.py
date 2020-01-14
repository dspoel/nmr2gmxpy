import Restraint
import test_atomno

class Orientation_restraint (Restraint.Restraint):
    def __init__(self,data_array):
        Restraint.Restraint.__init__(self, data_array)
        self.id = data_array[0]
        
        self.residue_1 = int(data_array[1])
        self.comp_id_1 = data_array[2]
        self.atom_id_1 = data_array[3]
        
        self.residue_2 = int(data_array[4])
        self.comp_id_2 = data_array[5]
        self.atom_id_2 = data_array[6]
        
        self.RDC = data_array[7]
        
        self.group_1 = 0
        self.group_2 = 0
        
        #value for force constant. Always 1?
        self.fac = 1.0
        
    def replace_atoms_names_and_groups(self):
        #replacing atom names by using atoms names and residue names 
        #and assigns nuber of hydogens in the ME_group1 and ME_group2
        #for example, ME_group1 = 3 if methyle group, 2 if methylene group and 1 if methine group 
        # for more info see test_atomno.py
        self.atom_id_1, self.group_1 = test_atomno.atom_replace(self.atom_id_1, self.comp_id_1)
        self.atom_id_2, self.group_2 = test_atomno.atom_replace(self.atom_id_2, self.comp_id_2)
        
    def write_header_in_file(self, fp):
        fp.write(";    ai\t    aj\t  type\t  exp.\t label\t alpha\tconst.\t  obs.\tweight\n")
        fp.write(";      \t      \t      \t      \t      \t   Hz \t nm^3 \t   Hz \t Hz^-2\n\n")
    
    def write_data_in_file(self, fp, my_number):
        atom_1 = test_atomno.get_atomno(self.residue_1, self.atom_id_1)
        atom_2 = test_atomno.get_atomno(self.residue_2, self.atom_id_2)
        alpha = 3 #assign value for alpha
        const = 6.083 #assign value for constant
        weight = 1.0 # assign value for weight
        type_orientation = 1
        exp = 1
        fp.write("%6s\t%6s\t%6s\t%6s\t%6s\t%6s\t%6s\t%6s\t%6s\n" %
                (atom_1, atom_2, type_orientation, exp, my_number+1,
                alpha, const, self.RDC, weight))
        



