import sys
from fractions import Fraction

sys.setrecursionlimit(1000000)

###########################

literals = {}

bv_map = {}
bounds_list = []

###########################

def head(v):
    return v[0]

def tail(v):
    return v[1:]

def make_ineq(op,lhs,rhs):
    return tuple(iter([op,lhs,rhs]))

def fst(ineq):
    return ineq[0]

def snd(ineq):
    return ineq[1]

def thd(ineq):
    return ineq[2]

def negIneq(ineq):
    return make_ineq("<",mult(snd(ineq), Fraction("-1")), mult(thd(ineq), Fraction("-1")))

def map_L(bv):
    if bv[0] == "-":
        return negIneq(bv_map.get(bv[1:]))
    else:
        return bv_map.get(bv)

def add(m1,m2):
    return {k : m1.get(k,0) + m2.get(k,0) for k in list(m1) + list(m2)} # list(m1) gets the keys of m1

def mult(m1,c):
    return {k : m1.get(k,0) * c for k in m1}

def value(m):
    for key in m:
        if key != "1" and m.get(key) != Fraction("0"):
            sys.exit("False")
    return m.get("1")

###########################

literalsFile = open("input.literals","r") # open file in read mode
ineqMap = open("input.laIneq","r") # open file in read mode
bounds = open("proof.liaTheory","r") # open file in read mode

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

for line in ineqMap.readlines():
    line_split = line.split()
    
    reachedConst = False
    reachedVar = False
    v_const = []
    v_var = []
    
    for i in range(0,len(line_split)):
        if i == 0:
            bv = line_split[i]
        elif line_split[i] == ";":
            continue
        elif line_split[i] == "[" and not reachedConst:
            reachedConst = True
        elif line_split[i] == "[" and not reachedVar:
            reachedVar = True
        elif line_split[i] == "]":
            continue
        elif reachedConst and not reachedVar:
            v_const.append(Fraction(line_split[i]))
        elif reachedConst and reachedVar:
            v_var.append(line_split[i])
        else:
            sys.exit("Error: reading lraIneq.map, invalid token: " + line_split[i])

    bv_map[bv] = make_ineq("<=",dict(zip(["0"],[Fraction("0")])),dict(zip(v_var[0:],v_const[0:])))

for line in bounds.readlines():
    line_split = line.split()

    for i in range(0,len(line_split)):
        if i == 0:
            ub = literals[line_split[i]]
        elif i == 1:
            lb = literals[line_split[i]]
        else:
            sys.exit("Error: reading liaTheory.proof, invalid format.")

    bounds_list.append([ub,lb])

literalsFile.close()
ineqMap.close()
bounds.close()

###########################

def checkBound(ub, lb):
    validStep = True

    validStep = validStep and list(thd(map_L(lb))) == list(thd(map_L(ub))) # check if the variables are the same, list(m) gets the keys of m

    for k in list(thd(map_L(lb))): # check if the variable coefficients are the complement of each other
        if not k == "1":
            validStep = validStep and thd(map_L(lb))[k] * -1 == thd(map_L(ub))[k]

    validStep = validStep and thd(map_L(lb))["1"] * -1 == thd(map_L(ub))["1"] + 1 # check if -lb = ub + 1

    return validStep

def checkProof():
    proofValid = True
    for i in bounds_list:
        proofValid = proofValid and checkBound(i[0], i[1])
    return proofValid

###########################

print(checkProof())
