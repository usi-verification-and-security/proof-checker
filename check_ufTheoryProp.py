literals = {}
equalitiesRefs = {}
distinctsRefs = {}

prop_set = set()
theory_set = set()

###########################

true = set()
true.add("0")
true = frozenset(true)

false = set()
false.add("3")
false = frozenset(false)

def negateLit(lit):
    if lit[0] == "-": return lit[1:]
    else: return "-" + lit

###########################

literalsFile = open("input.literals","r") # open file in read mode
ufFile = open("input.uf","r") # open file in read mode
propFile = open("input.ufTheoryProp","r") # open file in read mode
theoryFile = open("proof.ufTheory","r") # open file in read mode

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

for line in ufFile.readlines():
    line_split = line.split()

    args = set()

    for i in range(0,len(line_split)):
        if i == 0:
            termRef = line_split[i]
        elif i == 1:
            isEq = (True if line_split[i] == "=" else False)
            isDistinct = (True if line_split[i] == "distinct" else False)
        elif i > 1:
            args.add(line_split[i])

    if isEq: equalitiesRefs[frozenset(args)] = termRef
    if isDistinct: distinctsRefs[frozenset(args)] = termRef

for line in propFile.readlines():
    line_split = line.split()
    
    clause = set()
    
    for i in range(0,len(line_split)):
        clause.add(line_split[i])

    prop_set.add(frozenset(clause))

for line in theoryFile.readlines():
    line_split = line.split()

    if len(line) == 1: continue
    if line_split[0] != "(h": continue

    clause = set()
    hasRef = True; # flag to check if the RHS of the implication is "true = false", which does not have a PTRef

    for i in range(1,len(line_split)):
        equality = frozenset(line_split[i].replace("[","").replace("]","").replace(","," ").split())

        if true.issubset(equality) and false.issubset(equality):
            continue
        elif true.issubset(equality):
            ref = line_split[i].replace("[","").replace("]","").replace(","," ").split()
            ref.remove("0")
            clause.add(negateLit(literals[ref[0]]))
        elif false.issubset(equality):
            ref = line_split[i].replace("[","").replace("]","").replace(","," ").split()
            ref.remove("3")
            clause.add(literals[ref[0]])
        else:
            if i == 1:
                isDistinct = False
                for key in distinctsRefs.keys():
                    if equality.issubset(key):
                        clause.add(negateLit(literals[distinctsRefs[key]]))
                        isDistinct = True
                if not isDistinct: clause.add(literals[equalitiesRefs[equality]])
            else:
                isDistinct = False
                # Here we use the PTRefs of the equalities, not the distinct statements
                #for key in distinctsRefs.keys():
                #    if equality.issubset(key):
                #        clause.add(literals[distinctsRefs[key]])
                #        isDistinct = True
                if not isDistinct: clause.add(negateLit(literals[equalitiesRefs[equality]]))

    theory_set.add(frozenset(clause))

literalsFile.close()
ufFile.close()
propFile.close()
theoryFile.close()

###########################

print(prop_set.issubset(theory_set))
