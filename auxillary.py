import os


def find_assign(pdb_id, keywords):
    key = []
    counter=1
    # print(pdb_id)
    f = open('data_base/'+pdb_id+'.mr', 'r')
    lines = f.read()
    for i in range(0, len(keywords)):
        key.append(lines.find(keywords[i]))
        # print key[-1]

    # print max(key)
    if max(key) < 0:
        # os.system('rm data_base/'+pdb_id+'.pdb')
        # os.system('rm data_base/'+pdb_id+'.mr')
        counter=0
    
    return counter

