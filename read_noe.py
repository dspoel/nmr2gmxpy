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