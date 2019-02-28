

def check_category_type1(line):
    hydrogen_keywords = ["H", "h"]
    atom_keywords = ["name", "atomn"]    
    hydrogen_flag = 0
    for i, string in enumerate(line.split()):
        if any(x in string for x in atom_keywords) == True:
            if any(x in line.split()[i+1] for x in hydrogen_keywords) == True:
                hydrogen_flag = 1
            else:
                hydrogen_flag = 0
                
    # if hydrogen_flag == 1:
    #     print("True")

#     return True

# def check_category_type2(line):
#     return True

# def check_category_type3(line):
#     return True




# with open('mr.mr', 'r') as fn:
#     for line in    fn:
#         print line.split()
#         for i, string in enumerate(line.split()):
#             if "resn" in string:
#                 # print i, string
#                 print line.split()[i+1]
#             # print line.find("resn")
#         # print line.split().find("resn")