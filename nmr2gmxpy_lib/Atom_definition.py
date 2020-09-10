#   Copyright 2020 David van der Spoel
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

def NMRStarNelements():
    # Has to return the number of elements in the list returned below
    return 6

def NMRStarNames(atom_no):
    # Prepare a list of strings to extract from a NMR Star file
    names = [ 'PDB_residue_no_', 'Comp_ID_', 'Atom_ID_', 'Seq_ID_', 'PDB_strand_ID_', 'Comp_index_ID_' ]
    for n in range(len(names)):
        names[n] += str(atom_no)
    return names
        
class Atom_definition():
    def __init__(self, res_id, res_name, atom_name, chain_id):
        self.res_id    = int(res_id)
        self.res_name  = res_name
        self.chain_id  = chain_id
        self.atom_name = atom_name
        self.group     = 1
        self.atom_id   = None

    @classmethod
    def fromList(self, data):
        if data[4] != ".":
            chain = data[4]
        else:
            chain = '.' #data[3]
        if data[0] != ".":
            resid = data[0]
        else:
            resid = data[5]
        return self(resid, data[1], data[2], chain)
    def __eq__(self, other):
        return ((self.chain_id  == other.chain_id or
                 self.chain_id == ' ' or other.chain_id == '.') and
                self.res_id    == other.res_id and
                self.res_name  == other.res_name and
                self.atom_name == other.atom_name)
    def setName(self, atom_name):
        self.atom_name = atom_name
    def setAtomId(self, atom_id):
        self.atom_id = atom_id
    def atomId(self):
        return self.atom_id
    def setGroup(self, group):
        self.group = group
    def string(self):
        return self.chain_id + "-" + self.res_name + str(self.res_id) + "-" + self.atom_name

