#!/usr/bin/env python3

import argparse, os
# templates = [
#  [ "HA#", "HA3", "HA2" ],
#  [ "HA*", "HA3", "HA2" ],
#  [ "HB#",  "HB3", "HB2"   ],
#  [ "HB*",  "HB3", "HB2"   ],
#  [ "HG#",  "HG",         "HG1", "HG2",  "HG11", "HG12", "HG13", "HG21", "HG22", "HG23"  ],
#  [ "HG*",  "HG",         "HG1", "HG2",  "HG11", "HG12", "HG13", "HG21", "HG22", "HG23"  ],
#  [ "HG1#", "HG11",  "HG12", "HG13"  ],
#  [ "HG1*", "HG11",  "HG12", "HG13"  ],
#  [ "HG2#", "HG21",  "HG22", "HG23"  ],
#  [ "HG2*", "HG21",  "HG22", "HG23"  ],
#  [ "HD#",  "HD11", "HD12", "HD13", "HD21", "HD22", "HD23" ],
#  [ "HD*",  "HD11", "HD12", "HD13", "HD21", "HD22", "HD23" ],
#  [ "HD1#", "HD11",  "HD12"  ],
#  [ "HD1*", "HD11",  "HD12"  ],
#  [ "HD2#", "HD21",  "HD22"  ],
#  [ "HD2*", "HD21",  "HD22"  ],
#  [ "HE#",  "HE1",  "HE2"   ],
#  [ "HE*",  "HE1",  "HE2"   ],
#  [ "HH#",  "HH11",  "HH12", "HH21", "HH22" ],
#  [ "HH*",  "HH11",  "HH12", "HH21", "HH22" ],
#  [ "HZ#",  "HZ1", "HZ2",  "HZ3"   ],
#  [ "HZ*",  "HZ1", "HZ2",  "HZ3"   ],
#  [ "HN",   "H" ]
# ]

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mrfile", help="MR file",   type=str,
        default=None)
    parser.add_argument("-p", "--pdbfile", help="PDB file with correct GROMACS atom numbering.", type=str,
        default=None)
    parser.add_argument("-o", "--itpfile", help="ITP file", type=str,
        default="mr.itp")

    args = parser.parse_args()
    return args

class AtomNomTable:
    def __init__(self):
        gmxdata = os.environ["GMXDATA"]
        if not gmxdata:
            print("Please source a suitable GROMACS installation")
            exit(1)
        # tbl = open(gmxdata + "/top/atom_nom.tbl", "r")
        tbl = open("atom_nom.tbl", "r")
        self.table = []
        for line in tbl:
            if line.find("@") < 0:
                words = line.split()
                if len(words) == 4:
                    self.table.append([words[0], words[1], words[2], words[3]])
        self.table.sort(key=lambda x: (x[0], x[1]))
        tbl.close()
    
    def lookup(self, resnm, atomnm):
        list_nm = []
        # print(resnm, atomnm)
        for t in self.table:
            # print(t[0], t[1], t[2],t[3])
            if t[0] == resnm and t[1] == atomnm:
                list_nm.append(t[3])
        return list_nm
    
    # def lookup(self, resnm, atomnm):
    #     for t in self.table:
    #         if t[0] == resnm and t[1] == atomnm:
    #             return expand(self, resnm, t[4])
    #     return None
        
class MyAtom:
    def __init__(self, line):
        self.atomnr = int(line[7:11])
        self.atomnm = line[11:16].strip()
        self.resnm  = line[16:21].strip()
        self.resid  = int(line[22:26])

    # def print(self):
    #     print("%d %s %s %d" % ( self.atomnr, self.atomnm, 
    #                             self.resnm, self.resid ) )

class MyPdb:
    def __init__(self, filenm):
        fn = open(filenm, "r")
        self.pdb_atoms = []
        for line in fn:
            if line.find("ATOM") == 0 or line.find("HETATM") == 0:
                ma = MyAtom(line)
                self.pdb_atoms.append(ma)
#                ma.print()
        fn.close()
        
    def atoms(self):
        return self.pdb_atoms
    
def get_residue_atom_list(str):
    ral = []
    for s in str.split("or"):
        s = s.replace("(", "", 2)
        s = s.replace(")", "", 2)
        words = s.split()
        if len(words) == 5:
            ral.append((int(words[1]), words[4]))
    return ral

def lookup_atomid(resid, atom, pdb, an_tab):
    for p in pdb.atoms():        
        if (p.resid == resid):
            # print(p.resnm, atom)
            atomx = an_tab.lookup(p.resnm, atom)
            # print(atomx)
            # print(p.atomnm, atomx[0])
            if p.atomnm == atomx[0]:
                if len(atomx) == 1:
                    # print(p.atomnm)
                    # print([p.atomnr])
                    return [p.atomnr]
                else:      
                    # print(list(range(p.atomnr, p.atomnr+len(atomx))))              
                    return list(range(p.atomnr, p.atomnr+len(atomx)))

    print("Can not find resid %d atom %s" % ( resid, atom ))
    exit(1)

class Noe:
    def __init__(self, line):
        ll         = line.find("((")
        lr         = line.find("))")
        lefthand   = line[ll+2:lr]
        rl         = line[lr+1:].find("((")
        rr         = line[lr+1:].find("))")
        righthand  = line[lr+3+rl:lr+1+rr]
        dist_line  = line[lr+3+rr:].split()
        self.dd    = 0.1*float(dist_line[0])
        self.dm    = 0.1*float(dist_line[1])
        self.dp    = 0.1*float(dist_line[2])
        self.low   = self.dd - self.dm
        self.high1  = self.dd + self.dp
        self.high2  = self.high1 + 1
        self.left  = get_residue_atom_list(lefthand)
        self.right = get_residue_atom_list(righthand)
        
    def atoms_left(self):
        return self.left
    def atoms_right(self):
        return self.right
    def print_(self, fn, pdb_atoms, an_tab, dict ):
        for rall in self.left:
            # print(rall[0], rall[1])
            ai = lookup_atomid(rall[0], rall[1], pdb_atoms, an_tab)
            for ralr in self.right:
                aj = lookup_atomid(ralr[0], ralr[1], pdb_atoms, an_tab)                
                for i in range(0, len(ai)):
                    for j in range(0, len(aj)):
                        temp = {}
                        aii = min(ai[i], aj[j])
                        ajj = max(ai[i], aj[j])
                        temp[aii, ajj] = [1, 1, self.low, self.high1, self.high2, 1.0]
                        # print('temp: ',temp)
                        dictionary.update(temp)
                        # print('length: ',len(dictionary))

                        # fn.write("%5d  %5d %1d %1d %1d %f %f  %f %1f\n" % ( ai[i], aj[j], 1, index, 1, self.low, self.high1, self.high2, 1.0])

        
            # print((key[0], key[1], values[0], values[1],values[2],values[3],values[4],values[5],values[6]))


                          
def read_noe(filenm):
    fn       = open(filenm, "r")
    section  = None
    noe_list = []
    for line in fn:
        if line.find("*") == 0:
            continue
        elif line.find("NOE RESTRAINTS") >= 0:
            section = "noe"
        elif line.find("H-BOND RESTRAINTS") >= 0:
            section = "hbond"
        elif section and section == "noe":
            if line.find("assign") >= 0:                
                if line.find("((") >= 0:                
                    noeline = line.strip()
                    while line.find('!') == -1:
                        line = next(fn)
                        noeline = noeline + " " + line.strip()
                    # print(noeline)
                else:
                    noeline = line.strip()
                noe_list.append(Noe(noeline))
    fn.close()
    return noe_list
    
# Here the fun starts    
if __name__ == '__main__':
    args  = parseArguments()

    if args.mrfile and args.pdbfile:
        dictionary = {}
        an_tab    = AtomNomTable()
        pdb_atoms = MyPdb(args.pdbfile)
        noe_list  = read_noe(args.mrfile)
        itp = open(args.itpfile, "w")
        itp.write(" [ distance_restraints ]\n")
        itp.write("; Read an xplor distance restraint file %s\n" % (args.mrfile))
        itp.write("; %s was for the atom numbers\n" % (args.pdbfile))
        index = 0
        key_prev=0
        for n in noe_list:
            print(n)
            n.print_(itp, pdb_atoms, an_tab, dictionary )
        for keys, values in sorted(dictionary.items()):
            # if key_prev != keys[0]:
            #     key_prev = keys[0]
            itp.write("%5d %5d  %1d %1d %1d %f %f  %f %f\n" % (keys[0], keys[1], values[0], index, values[1],values[2],values[3],values[4],values[5]) )
            index = index + 1
        itp.close()
