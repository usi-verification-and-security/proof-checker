literals = {}

dratProp_set = set()
lraProp_set = set()

###########################

literalsFile = open("input.literals","r") # open file in read mode
dratProp = open("input.lraTheoryProp","r") # open file in read mode
lraProp = open("proof.lraTheory","r") # open file in read mode

for line in literalsFile.readlines():
    line_split = line.split()

    for i in range(0,len(line_split)):
        if i == 0:
            termRef = line_split[i]
        elif i == 1:
            lit = line_split[i]
        elif i > 1:
            sys.exit("Error: reading input.literals, invalid format.")

    literals[termRef] = lit

for line in dratProp.readlines():
    line_split = line.split()
    
    clause = set()
    
    for i in range(0,len(line_split)):
        clause.add(line_split[i])

    dratProp_set.add(frozenset(clause))

for line in lraProp.readlines():
    line_split = line.split()

    clause = set()
    reachedFC = False

    for i in range(0,len(line_split)):
        if line_split[i] == ";":
            reachedFC = True
        elif not reachedFC and line_split[i][0] == "-":
            clause.add("-" + literals[line_split[i][1:]])
        elif not reachedFC:
            clause.add(literals[line_split[i]])
        else:
            break

    lraProp_set.add(frozenset(clause))

literalsFile.close()
dratProp.close()
lraProp.close()

###########################

print(dratProp_set.issubset(lraProp_set))
