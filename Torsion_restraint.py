import Restraint
import test_atomno

class Torsion_restraint (Restraint.Restraint):
    def __init__(self,data_array):
        Restraint.Restraint.__init__(self, data_array)
        self.id = data_array[0]
        
        self.residue_1 = int(data_array[1])
        self.comp_id_1 = data_array[2]
        self.atom_id_1 = data_array[3]
        
        self.residue_2 = int(data_array[4])
        self.comp_id_2 = data_array[5]
        self.atom_id_2 = data_array[6]
        
        self.residue_3 = int(data_array[7])
        self.comp_id_3 = data_array[8]
        self.atom_id_3 = data_array[9]
        
        self.residue_4 = int(data_array[10])
        self.comp_id_4 = data_array[11]
        self.atom_id_4 = data_array[12]
        
        self.angle_lower_boundary = float(data_array[13])
        self.angle_upper_boundary = float(data_array[14])
        
        self.group_1 = 0
        self.group_2 = 0
        self.group_3 = 0
        self.group_4 = 0
        
        #value for force constant. Always 1?
        self.fac = 1.0
        
    def replace_atoms_names_and_groups(self):
        #replacing atom names by using atoms names and residue names 
        #and assigns nuber of hydogens in the ME_group1 and ME_group2
        #for example, ME_group1 = 3 if methyle group, 2 if methylene group and 1 if methine group 
        # for more info see test_atomno.py
        self.atom_id_1, self.group_1 = test_atomno.atom_replace(self.atom_id_1, self.comp_id_1)
        self.atom_id_2, self.group_2 = test_atomno.atom_replace(self.atom_id_2, self.comp_id_2)
        self.atom_id_3, self.group_3 = test_atomno.atom_replace(self.atom_id_3, self.comp_id_3)
        self.atom_id_4, self.group_4 = test_atomno.atom_replace(self.atom_id_4, self.comp_id_4)
        
    def write_header_in_file(self, fp):
        fp.write(";    ai\t    aj\t    ak\t    al\t  type\t   phi\t  dphi\t   fac\n\n")
        
    def write_data_in_file(self, fp, my_number):
        # g1,g2,g3 and g4 extra output from the fucntion atom_replace in module test_atomno.py
        # getting atom number from residue number and atom name
        atom_1 = test_atomno.get_atomno(self.residue_1, self.atom_id_1)
        atom_2 = test_atomno.get_atomno(self.residue_2, self.atom_id_2)
        atom_3 = test_atomno.get_atomno(self.residue_3, self.atom_id_3)
        atom_4 = test_atomno.get_atomno(self.residue_4, self.atom_id_4)
        phi = round(( self.angle_upper_boundary + self.angle_lower_boundary)/2.0, 2)
        dphi = round((self.angle_upper_boundary - self.angle_lower_boundary)/2.0, 2)
        fac = 1.0 # assign value for force constant
        fp.write("%6s\t%6s\t%6s\t%6s\t     1\t%6s\t%6s\t%6s\n" %(atom_1,atom_2,atom_3,atom_4,phi,dphi,self.fac))




