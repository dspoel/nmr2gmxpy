

line = "assi (( segid \"   A\" and resid 30   and name  HN  )) (( segid \"   A\" and resid 32   and name  HN  )) 3.070     1.270     1.270"

print line
assign_keywords = ["assi", "assign", "ASSIGN"]

print any(x in line for x in assign_keywords)