 #!/usr/bin/env python3

import argparse, os, subprocess
import auxillary as aux
import check_category as cat

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-gmx", "--gromacs_command" , help="",   type=str,  default="gmx")
    parser.add_argument("-data_base", "--data_base" , help="",   type=str,  default=None)
    parser.add_argument("-check_nmr", "--check_nmr" , help="",   type=str,  default=None)
    parser.add_argument("-read_nmr", "--read_nmr" , help="",   type=str,  default=None)
    parser.add_argument("-mrfile", "--mrfile", help="MR file",   type=str,
        default=None)
    parser.add_argument("-p", "--pdbfile", help="PDB file with correct GROMACS atom numbering.", type=str,
        default=None)
    parser.add_argument("-opt3", "--opt3" , help="",   type=str,  default=None)
    parser.add_argument("-opt4", "--opt4" , help="",   type=str,  default=None)
    parser.add_argument("-opt5", "--opt5" , help="",   type=str,  default=None)
    parser.add_argument("-opt6", "--opt6" , help="",   type=str,  default=None)
    parser.add_argument("-opt7", "--opt7" , help="",   type=str,  default=None)
    parser.add_argument("-opt8", "--opt8" , help="",   type=str,  default=None)
    parser.add_argument("-opt9", "--opt9" , help="",   type=str,  default=None)


    args = parser.parse_args()
    return args


def find_2nd(string, substring):
   return string.find(substring, string.find(substring) + 1)

def check_cat_type1(line):
    c = 0
    a = 0
    text = line.split()
#   r = re.find('or')
    for i, words in enumerate(text):
        if any(r in words for r in atom_keywords) == True:
            a+=1
        if any(n in words for n in atom_keywords) == True:
            z = list(text[i+1])
    #       print("z:", z)
            if any(h in z[0] for h in atomsNOE) == True:
                c+=1
    if c == a:
        return True

def check_cat_type2(line):
    c = 0
    a = 0
    text = line.split()
    for i, words in enumerate(text):
        if any(r in words for r in atom_keywords) == True:
            a+=1
        if any(n in words for n in atom_keywords) == True:
            z = list(text[i+1])
            if any(h in z[0] for h in atomsDihedral) == True:
                c+=1
    if c == a:
        return True

class AtomNomTable:
    def __init__(self):
        # gmxdata = os.environ["GMXDATA"]
        # if not gmxdata:
        #     print("Please source a suitable GROMACS installation")
        #     exit(1)
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
        # print "resnm: ", resnm
        # print "atomnm: ", atomnm
        for t in self.table:
            if t[0] == resnm and t[1] == atomnm:
                # print "t: ", t
                list_nm.append(t[3])
        # print "list_nm: ", list_nm  
        return list_nm


class MyAtom:
    def __init__(self, line):
        # print line
        self.atomnr = int(line[7:11])
        self.atomnm = line[11:16].strip()
        self.resnm  = line[16:21].strip()
        self.resid  = int(line[22:26])
        # print self.atomnr, self.atomnm, self.resnm, self.resid

    def print_(self):
        print("%d %s %s %d" % ( self.atomnr, self.atomnm, 
                                self.resnm, self.resid ) )


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



def lookup_atomid(resid, atom, pdb, an_tab):
    # print "resid: ", resid
    no_res = False
    for p in pdb.atoms():
        if (p.resid == resid):
            atomx = an_tab.lookup(p.resnm, atom)
            if atomx != []:
                if p.atomnm == atomx[0]:
                    if len(atomx) == 1:
                        return [p.atomnr]
                    else:
                        return range(p.atomnr, p.atomnr+len(atomx))
            else:
                no_res = True
            
    # if no_res == True:

        # print("Bug report: Can not find resid %d atom %s" % ( resid, atom ))
                # return None
                # exit(1)

def makePairs( pairs_list ):
    pairs = []
    firstAtom = ""
    secondAtoms = []
    # words = line.split()
    for i in range( len(pairs_list) ):
        w = pairs_list[i]
        isLastWord = i == len(pairs_list)-1
        if w != 'or':
            if (not isLastWord) and (pairs_list[i+1] != 'or'):
                pairs.append([w,pairs_list[i+1]])

            if ((not isLastWord) and (pairs_list[i+1] == 'or')) or (i > 0 and pairs_list[i-1] == 'or'):
                secondAtoms.append(w)
            else:
                firstAtom = w
                    

    if len(pairs) > 1:
        return pairs

    pairs = []
    # print secondAtoms
    # print firstAtoms
    for a in secondAtoms:
        pairs.append( [firstAtom, a] )

    return pairs

class Noe:
    def __init__(self, line, pdb_atoms, an_tab, noe_dict, indx, pdb_id):
        with open("data_base/"+pdb_id+".bug", 'a') as bug:
            line_flag = True        
            original_line = line
            atom_keywords = ['name', 'atomnm']
            res_keywords = ['resi', 'resid']
            line = line.replace('OR', 'or')
            line = line.replace('Or', 'or')
            line = line.replace('##', '#')
            line = line.replace('**', '*')
            line = line.replace('))', ')')
            line = line.replace('((', '(')
            pairs_list, res_data = [], []
            # index_p = -1
            # index_e = -1
            # index_p =  find_2nd(line, ")")
            # index_e =  line.rfind("!")

            line_list = line.split()
            if line.find("!") > -1 :
                if line.find("weight") > -1:
                    for i in range(len(line_list)):
                        if line_list[i] == "weight":
                            res_data.append(line_list[i-3])
                            res_data.append(line_list[i-2])
                            res_data.append(line_list[i-1])
                else:
                    for i in range(len(line_list)):
                        if line_list[i] == "!":
                            res_data.append(line_list[i-3])
                            res_data.append(line_list[i-2])
                            res_data.append(line_list[i-1])
            else:
                res_data.append(line_list[-3])
                res_data.append(line_list[-2])
                res_data.append(line_list[-1])
                # print line_list[-3], line_list[-2], line_list[-1]

            # print index_p
            # print index_e
            # if index_p != -1:
            #     if index_e != -1 and index_e > index_p:
            #         res_data_temp = line[index_p+1 : index_e-1]
            #         # print res_data_temp
            #     else:
            #         res_data_temp = line[index_p+1:]
            # res_data_temp = res_data_temp.split(' ')
            # # print res_data_temp
            # while '' in res_data_temp:
            #     res_data_temp.remove('')
            # #I need a check here so the next line doesnt kill if there is no triple written 
            # res_data = res_data_temp[0:3]
            # # if res_data != []:
            dd = 0.1*float(res_data[0])
            dm = 0.1*float(res_data[1])
            dp = 0.1*float(res_data[2])
            low = dd - dm
            high1 = dd + dp
            high2 = high1 + 1
            line = line.replace(')', '')
            line = line.replace('(', '')
            ai, aj = [],[]
            res=""
            atom=""
            # print res_keywords
            # print atom_keywords
            for i, word in enumerate(line.split()):
                # print word
                if word in res_keywords:
                    # print word
                    # line_list.append(line.split()[i+1])
                    res=line.split()[i+1]
                    # indices.append(i)
                if word in atom_keywords:
                    # line_list.append(line.split()[i+1])
                    atom=line.split()[i+1]
                if word == "or":
                    pairs_list.append(line.split()[i])
                if res != "" and atom != "":
                    pairs_list.append([res, atom])
                    res=""
                    atom=""
            # print pairs_list[0][0]
        # print makePairs(pairs_list)
            if len(pairs_list) == 2:
                # print original_line
                # print pairs_list
                ai_el = lookup_atomid(int(pairs_list[0][0]),pairs_list[0][1], pdb_atoms, an_tab)
                aj_el = lookup_atomid(int(pairs_list[1][0]),pairs_list[1][1], pdb_atoms, an_tab)
                #what if it's None
                if ai_el != None and aj_el != None:
                    ai.extend(ai_el)
                    aj.extend(aj_el)
            else:
                # print original_line
                pairs_list = makePairs(pairs_list)
                for i in range(len(pairs_list)):
                    ai_el = lookup_atomid(int(pairs_list[i][0][0]),pairs_list[i][0][1], pdb_atoms, an_tab)
                    aj_el = lookup_atomid(int(pairs_list[i][1][0]),pairs_list[i][1][1], pdb_atoms, an_tab)
                #     #what if it's None
                    if ai_el != None and aj_el != None:
                        ai.extend(ai_el)
                        aj.extend(aj_el)

            print ai, aj
            if ai != [] and aj != []:
                # print len(ai), len(aj)
                for i in range(0, len(ai)):
                    for j in range(0, len(aj)):
                        temp = {}
                        aii = min(ai[i], aj[j])
                        ajj = max(ai[i], aj[j])
                        print indx
                        temp[aii, ajj] = [1, indx, 1, low, high1, high2, 1.0]
                        # temp[aii, ajj] = [1, 1, 1, 1, 1, 1.0]
                        # print temp
                        noe_dict.update(temp)
            else:
                bug.write("unresolved line: "+original_line+"\n")
class Dihedral:
    def __init__(self, line, pdb_atoms, an_tab, dih_dict):
        line_flag = True 
        # print "Start-----------------------------"
        original_line = line
        line_list, a = [], []
        atom_keywords = ['name', 'atomnm']
        res_keywords = ['resi', 'resid']
        index_p =  line.rfind(")")        
        dih_data_temp = line[index_p+1:]
        dih_data_temp = dih_data_temp.split(' ')
        while '' in dih_data_temp:
            dih_data_temp.remove('')
        # print float(dih_data_temp[0])
        # print float(dih_data_temp[1])
        # print float(dih_data_temp[2])
        # print float(dih_data_temp[3])

        # dih_data = dih_data_temp[0:3]
        
        line = line.replace('))', '')
        line = line.replace(')', '')
        line = line.replace('((', '')
        line = line.replace('(', '')
        # print line
        for i, words in enumerate(line.split()):
            if any(n in words for n in res_keywords) == True:
                line_list.append(line.split()[i+1])
                # indices.append(i)
            if any(n in words for n in atom_keywords) == True:
                line_list.append(line.split()[i+1])
        print line_list
        a.extend(lookup_atomid(int(line_list[0]),line_list[1], pdb_atoms, an_tab))
        a.extend(lookup_atomid(int(line_list[2]),line_list[3], pdb_atoms, an_tab))
        a.extend(lookup_atomid(int(line_list[4]),line_list[5], pdb_atoms, an_tab))
        a.extend(lookup_atomid(int(line_list[6]),line_list[7], pdb_atoms, an_tab))
        # print a
        temp = {}
        temp[a[0], a[1], a[2], a[3]] = [float(dih_data_temp[0]), float(dih_data_temp[1]), float(dih_data_temp[2]), float(dih_data_temp[3])]
        dih_dict.update(temp)
        


                    


if __name__ == '__main__':
    args  = parseArguments()
    assign_keywords = ["assi", "assign", "ASSIGN"]
    junk_char = ["*", "#", "!"]
    junk_words = ["FILETERM", "Start", "START", "start", "MODEL", "Entry", "Model", "RESTRAINTS"]
    res_id = ["resid", "resi", "resn", "((resid", "(resid", "((resi", "(resi", "((resn", "(resn"]
    atom_keywords = ['name', 'atomnm']
    atomsNOE = ['H','h']
    atomsDihedral = ['C', 'N', 'c', 'n']
    good_pdb = 0

    if args.data_base:
        os.system('ls data_base/*.pdb > temp_pdb')
        num_pdb_database = subprocess.Popen(['cat temp_pdb | wc -l'], stdout=subprocess.PIPE, shell=True).communicate()[0].decode('utf-8').strip()
        with open('temp_pdb', 'r') as fn:
            with open('pdb_id.txt', 'w') as gn:
                for line1 in fn:
                    line2 = line1.split('/')
                    pdb_id = line2[1].split('.pdb')
                    gn.write(pdb_id[0]+'\n')
        os.system('rm temp_pdb')

    if args.check_nmr:
        with open('good_pdb.txt', 'w') as gn:
            with open('pdb_id.txt', 'r') as fn:
                for line in fn:
                    pdb_id = line.rstrip('\n')
                    good_pdb=good_pdb+aux.find_assign(pdb_id, assign_keywords)
                    if aux.find_assign(pdb_id, assign_keywords) == 1:
                        gn.write(pdb_id+"\n")
            good_pdb_portion = float(good_pdb)/float(num_pdb_database)
            # print(str(good_pdb_portion*100)+"% of mr files have the \"assign\" keyword")

    if args.read_nmr:
        an_tab    = AtomNomTable()
        pdb_atoms = MyPdb("data_base/"+pdb_id+".pdb")
        with open('good_pdb.txt', 'r') as fn:
            for line in fn:
                pdb_id = line.rstrip('\n')
                if aux.find_assign(pdb_id, assign_keywords) == 1:
                    print "data_base/"+pdb_id+".mr"
                    os.system("rm data_base/"+pdb_id+".bug")
                    if args.mrfile:
                        noe_dict = {}
                        dih_dict = {}
                        # os.system("sed -E \"\" $\'s/\\\\\\r/\\\\\\n/g\' data_base/"+pdb_id+".mr ")
                        counter = 0
                        # print pdb_id
                        with open("data_base/"+pdb_id+".mr", 'r') as gn:
                            indx=0
                            lines = gn.readlines()
                            i=0
                            while i < len(lines):
                                newline = ""
                                # print lines[i]
                                if any(x in lines[i] for x in assign_keywords) == True and any(x in lines[i] for x in junk_words) != True and any(x in lines[i][0] for x in junk_char) != True:                                     
                                    counter = counter +1
                                    newline = lines[i].strip("\n")
                                    while i < len(lines)-1 and (any(x in lines[i+1] for x in assign_keywords) != True and any(x in lines[i+1] for x in junk_words) != True and any(x in lines[i+1][0] for x in junk_char) != True ):
                                        i = i+1
                                        newline = newline + ' ' + lines[i].strip("\n")
                                # print newline
                                if newline != "":
                                    if check_cat_type1(newline) == True:
                                        # print newline
                                        Noe(newline, pdb_atoms, an_tab, noe_dict, indx, pdb_id)
                                        indx = indx+1
                                    # elif check_cat_type2(newline) == True:
                                    #     Dihedral(newline, pdb_atoms, an_tab, dih_dict)
                                    # else:
                                    #     with open("data_base/"+pdb_id+".bug", 'a') as bug:
                                    #         bug.write("unresolved line: "+ newline+"\n")

                                        # print "NONE"                                    

                                i = i+1

                        # with open("data_base/"+pdb_id+"-dihedral.itp", 'w') as itp:
                        #     itp.write(" [ dihedral_restraints ]\n")
                        #     for keys, values in dih_dict.items():
                        #         itp.write("%5d %5d %5d %5d  %.3f %.3f  %.3f %.3f\n" % (keys[0], keys[1], keys[2], keys[3], values[0], values[1],values[2],values[3]) )

                        with open("data_base/"+pdb_id+"-disre.itp", 'w') as itp:
                            itp.write(" [ distance_restraints ]\n")
                            for keys, values in sorted(noe_dict.items(), key=lambda x:x[1]):
                                itp.write("%5d %5d  %1d %1d %1d %.3f %.3f  %.3f %.3f\n" % (keys[0], keys[1], values[0], values[1],values[2],values[3],values[4],values[5], values[6]) )
                            
######################################################################################################


    # if args.mrfile and args.pdbfile:
        # dictionary = {}
        # an_tab    = AtomNomTable()
        # pdb_atoms = MyPdb(args.pdbfile)
        # noe_list  = read_noe(args.mrfile)


    # with open('pdb_list.txt', 'r') as fn:
        # for pdb in fn:
            # if args.opt2:
            #     os.system('rm '+pdb+'.top')
            #     os.system(args.gromacs_command+' pdb2gmx '+' -f '+pdb+'.pdb'+' -o '+pdb+'.pdb'+' -p '+pdb+'.top'+' -ff '+args.force_field+' -water '+args.water_model+' -ignh ')
            # if args.opt3:
            #     # generate_disre_itp_file
            # if args.opt4:
            #     # add_disres_to_top_file
            # if args.opt5:
            #     # task5
            # if args.opt6:
            #     # task6
            # if args.opt7:
            #     # task7
            # if args.opt8:
            #     # task8
            # if args.opt9:
                # task9



#                 indices = [i for i, elem in enumerate(line_list) if 'or' in elem] 
#                 if indices != []:
#                     key= [(len(line_list) - len(indices))/2]+indices
#                     print key, line_list
#                     if len(key) == key[0]/2:
#                         index = [-1]+key[1:]
#                         for i in range(0, key[0]/2):
#                             ai,aj = [],[]
#                             ai_el = lookup_atomid(int(line_list[index[i]+1]),line_list[index[i]+2], pdb_atoms, an_tab)
#                             aj_el = lookup_atomid(int(line_list[index[i]+3]),line_list[index[i]+4], pdb_atoms, an_tab)
#                             if ai_el != None and aj_el != None:
#                                 ai.extend(ai_el)
#                                 aj.extend(aj_el)
#                             for i in range(0, len(ai)):
#                                 for j in range(0, len(aj)):
#                                     temp = {}
#                                     aii = min(ai[i], aj[j])
#                                     ajj = max(ai[i], aj[j])
#                                     temp[aii, ajj] = [1, indx, 1, low, high1, high2, 1.0]                    
#                                     noe_dict.update(temp)
# ########    ####################################################################################
#                     elif key == [3,2]:
#                         print key, line_list
#                         aj_el = lookup_atomid(int(line_list[5]),line_list[6], pdb_atoms, an_tab)
#                         aj.extend(aj_el)
#                         ai_el = lookup_atomid(int(line_list[0]),line_list[1], pdb_atoms, an_tab)
#                         if ai_el != None and aj_el != None:
#                             ai.extend(ai_el)
#                             aj.extend(aj_el)                    
#                         ai_el = lookup_atomid(int(line_list[3]),line_list[4], pdb_atoms, an_tab)
#                         if ai_el != None and aj_el != None:
#                             ai.extend(ai_el)
#                             aj.extend(aj_el)
# ########    ####################################################################################
#                     elif key == [3,4]:
#                         print key, line_list
#                         ai_el = lookup_atomid(int(line_list[0]),line_list[1], pdb_atoms, an_tab)                    
#                         aj_el = lookup_atomid(int(line_list[2]),line_list[3], pdb_atoms, an_tab)
#                         if ai_el != None and aj_el != None:
#                             ai.extend(ai_el)
#                             aj.extend(aj_el)                    
#                         aj_el = lookup_atomid(int(line_list[5]),line_list[6], pdb_atoms, an_tab)
#                         if ai_el != None and aj_el != None:
#                             ai.extend(ai_el)
#                             aj.extend(aj_el)                                                        
# ########    ####################################################################################
#                     elif key == [4,4,7]:
#                         print key, line_list
#                         ai_el = lookup_atomid(int(line_list[0]),line_list[1], pdb_atoms, an_tab)
#                         aj_el = lookup_atomid(int(line_list[2]),line_list[3], pdb_atoms, an_tab)
#                         if ai_el != None and aj_el != None:
#                             ai.extend(ai_el)
#                             aj.extend(aj_el)
#                         aj_el = lookup_atomid(int(line_list[5]),line_list[6], pdb_atoms, an_tab)
#                         if ai_el != None and aj_el != None:
#                             ai.extend(ai_el)
#                             aj.extend(aj_el)
#                         aj_el = lookup_atomid(int(line_list[8]),line_list[9], pdb_atoms, an_tab)
#                         if ai_el != None and aj_el != None:
#                             ai.extend(ai_el)
#                             aj.extend(aj_el)
# ########    ####################################################################################
#                     elif key == [4,2,5]:
#                         print key, line_list
#                         aj_el = lookup_atomid(int(line_list[8]),line_list[9], pdb_atoms, an_tab)
#                         ai_el = lookup_atomid(int(line_list[0]),line_list[1], pdb_atoms, an_tab)
#                         if ai_el != None and aj_el != None:
#                             ai.extend(ai_el)
#                             aj.extend(aj_el)
#                         ai_el = lookup_atomid(int(line_list[3]),line_list[4], pdb_atoms, an_tab)
#                         if ai_el != None and aj_el != None:
#                             ai.extend(ai_el)
#                             aj.extend(aj_el)
#                         ai_el = lookup_atomid(int(line_list[6]),line_list[7], pdb_atoms, an_tab)
#                         if ai_el != None and aj_el != None:
#                             ai.extend(ai_el)
#                             aj.extend(aj_el)
#                     else:
#                         # print "unordinary line, ", key, line_list
#                         bug.write("unresolved line: "+original_line+"\n")
#                 else:
#                     bug.write("unresolved line: "+original_line+"\n")
            # print "ai, aj: ", ai, aj