

key = []
pdb_id="5MSL"
keywords = ["assi", "assign", "ASSIGN"]

f = open('data_base/'+pdb_id+'.mr', 'r')
lines = f.read()
for i in range(0, len(keywords)):
    key.append(lines.find(keywords[i]))
    print key[-1]

if max(key) > 0:
    continue
else:
    rm 
