import sys

sys.setrecursionlimit(1000000)

###########################

literals = {}

pNodes = {}
rules = {}

cnfizedFormula = []

###########################

def make_pair(op1,op2):
    return tuple(iter([op1,op2]))

def make_triple(op1,op2,op3):
    return tuple(iter([op1,op2,op3]))

def fst(pNode):
    return pNode[0]

def snd(pNode):
    return pNode[1]

def thd(pNode):
    return pNode[2]

def operator(termRef):
    return fst(pNodes[termRef])

def literal(termRef):
    if snd(pNodes[termRef]) != "*": return snd(pNodes[termRef])
    else: return negateLit(literal(thd(pNodes[termRef])[0]))

def negateLit(lit):
    if lit[0] == "-": return lit[1:]
    else: return "-" + lit

###########################

literalsFile = open("input.literals","r") # open file in read mode
pNodesFile = open("input.pnodes","r") # open file in read mode
rulesFile = open("proof.cnfization","r") # open file in read mode
cnfFile = open("input.cnf","r") # open file in read mode

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

for line in pNodesFile.readlines():
    line_split = line.split()

    termRef = -1
    op = "none"
    termValue = 0
    children = []

    if len(line_split) == 1:
        op = "leaf"

    for i in range(0,len(line_split)):
        if i == 0:
            termRef = line_split[i]
        elif i == 1:
            op = line_split[i]
        elif i > 1:
            children.append(line_split[i])

    if termRef in literals:
        pNodes[termRef] = make_triple(op, literals[termRef], children)
    else:
        pNodes[termRef] = make_triple(op, "*", children)

for line in rulesFile.readlines():
    line_split = line.split()

    termRef = -1
    rule = "none"
    clauses = [] # clause indexes that is

    for i in range(0,len(line_split)):
        if i == 0:
            termRef = line_split[i]
        elif i == 1:
            rule = line_split[i]
        elif i > 1:
            clauses.append(line_split[i])

    rules[termRef] = make_pair(rule, clauses)

next(cnfFile) # skip header of cnf file
for line in cnfFile.readlines():
    line_split = line.split()

    clause = set()

    for i in range(0,len(line_split)):
        if line_split[i] != "0":
            clause.add(line_split[i])

    cnfizedFormula.append(frozenset(clause))

literalsFile.close()
pNodesFile.close()
rulesFile.close()
cnfFile.close()

###########################

def id(termRef):
    res = False
    if not fst(pNodes[termRef]) == "and" and not fst(pNodes[termRef]) == "or":
        res = frozenset([snd(pNodes[termRef])]) == cnfizedFormula[int(snd(rules[termRef])[0])-1] # -1 because lists are 0-based
    else:
        children = thd(pNodes[termRef])[:] # copy the list by value
        clause = []
        while len(children) > 0:
            if operator(children[0]) == operator(termRef):
                for child in thd(pNodes[children[0]]):
                    children.append(child)
            else:
                clause.append(literal(children[0]))
            children.pop(0)

        res = frozenset(clause) == cnfizedFormula[int(snd(rules[termRef])[0])-1] # -1 because lists are 0-based

    return res

def conj(termRef):
    if len(thd(pNodes[termRef])) < 2: return False
    clauses = set()
    clause = []

    for child in thd(pNodes[termRef]):
        clauses.add(frozenset([literal(child), negateLit(literal(termRef))]))
        clause.append(negateLit(literal(child)))
    clause.append(literal(termRef))
    clauses.add(frozenset(clause))

    cnfClauses = set()
    for c in snd(rules[termRef]):
        cnfClauses.add(cnfizedFormula[int(c)-1]) # -1 because lists are 0-based

    return clauses == cnfClauses

def disj(termRef):
    if len(thd(pNodes[termRef])) < 2: return False
    clauses = set()
    clause = []

    for child in thd(pNodes[termRef]):
        clauses.add(frozenset([negateLit(literal(child)), literal(termRef)]))
        clause.append(literal(child))
    clause.append(negateLit(literal(termRef)))
    clauses.add(frozenset(clause))

    cnfClauses = set()
    for c in snd(rules[termRef]):
        cnfClauses.add(cnfizedFormula[int(c)-1]) # -1 because lists are 0-based

    return clauses == cnfClauses

def xor(termRef):
    if len(thd(pNodes[termRef])) < 2: return False
    clauses = set()
    clause1 = []
    clause2 = []

    for c1 in thd(pNodes[termRef]):
        clauseTemp = []
        clauseTemp.append(literal(termRef))
        clauseTemp.append(literal(c1))
        for c2 in thd(pNodes[termRef]):
            if c1 != c2:
                clauseTemp.append(negateLit(literal(c2)))
        clauses.add(frozenset(clauseTemp))

        clause1.append(literal(c1))
        clause2.append(negateLit(literal(c1)))

    clause1.append(negateLit(literal(termRef)))
    clause2.append(negateLit(literal(termRef)))
    clauses.add(frozenset(clause1))
    clauses.add(frozenset(clause2))

    cnfClauses = set()
    for c in snd(rules[termRef]):
        cnfClauses.add(cnfizedFormula[int(c)-1]) # -1 because lists are 0-based

    return clauses == cnfClauses

def iff(termRef):
    if len(thd(pNodes[termRef])) < 2: return False
    clauses = set()
    clause1 = []
    clause2 = []

    for c1 in thd(pNodes[termRef]):
        clauseTemp = []
        clauseTemp.append(negateLit(literal(termRef)))
        clauseTemp.append(literal(c1))
        for c2 in thd(pNodes[termRef]):
            if c1 != c2:
                clauseTemp.append(negateLit(literal(c2)))
        clauses.add(frozenset(clauseTemp))

        clause1.append(literal(c1))
        clause2.append(negateLit(literal(c1)))

    clause1.append(literal(termRef))
    clause2.append(literal(termRef))
    clauses.add(frozenset(clause1))
    clauses.add(frozenset(clause2))

    cnfClauses = set()
    for c in snd(rules[termRef]):
        cnfClauses.add(cnfizedFormula[int(c)-1]) # -1 because lists are 0-based

    return clauses == cnfClauses

def ite(termRef): # Rule not implemented
    return False

def impl(termRef): # Rule not implemented
    return False

def deMorg(termRef):
    if fst(pNodes[termRef]) == "not":
        if fst(pNodes[thd(pNodes[termRef])[0]]) == "and":
            children = thd(pNodes[thd(pNodes[termRef])[0]])[:] # copy the list by value
            clause = []
            while len(children) > 0:
                if literal(children[0]) == "*" or operator(children[0]) == "and":
                    for child in thd(pNodes[children[0]]):
                        children.append(child)
                else:
                    clause.append(negateLit(literal(children[0])))
                children.pop(0)
            
            return frozenset(clause) == cnfizedFormula[int(snd(rules[termRef])[0])-1]
    return False

def applyRule(termRef):
    if   fst(rules[termRef]) == "Id":
        return id(termRef)
    elif fst(rules[termRef]) == "Conj":
        return conj(termRef)
    elif fst(rules[termRef]) == "Disj":
        return disj(termRef)
    elif fst(rules[termRef]) == "Xor":
        return xor(termRef)
    elif fst(rules[termRef]) == "Iff":
        return iff(termRef)
    elif fst(rules[termRef]) == "Ite":
        return ite(termRef)
    elif fst(rules[termRef]) == "Impl":
        return impl(termRef)
    elif fst(rules[termRef]) == "DeMorg":
        return deMorg(termRef)
    else:
        return False

def checkProof():
    proofValid = True
    for key in rules:
        proofValid = proofValid and applyRule(key)
        if not proofValid:
            break
    return proofValid

###########################

print(checkProof())
