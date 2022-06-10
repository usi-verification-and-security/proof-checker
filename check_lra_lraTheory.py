import sys
from fractions import Fraction

sys.setrecursionlimit(1000000)

###########################

literals = {}

bv_map = {}
conflict_list = []

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
conflicts = open("proof.lraTheory","r") # open file in read mode

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

for line in conflicts.readlines():
    line_split = line.split()

    reachedFC = False
    v_term = []
    v_termFC = []

    for i in range(0,len(line_split)):
        if line_split[i] == ";":
            reachedFC = True
        elif not reachedFC and line_split[i][0] == "-":
            v_term.append("-" + literals[line_split[i][1:]])
        elif not reachedFC:
            v_term.append(literals[line_split[i]])
        elif reachedFC:
            v_termFC.append(Fraction(line_split[i]))
        else:
            sys.exit("Error: reading lraTheory.proof, invalid token: " + line_split[i])

    conflict_list.append([v_term,v_termFC])

literalsFile.close()
ineqMap.close()
conflicts.close()

###########################

def check(v_bv, v_fc, ineq):
    if len(v_bv) != len(v_fc): # restriction checking
        sys.exit("Error: checking restriction -> v_bv: " + v_bv + ", v_fc: " + v_fc + ", ineq: " + ineq)
    elif len(v_bv) == 0: # base case
        return ineq
    else: # recursive case
        if fst(ineq) == "<":
            return check(tail(v_bv), tail(v_fc), make_ineq(fst(ineq), add(snd(ineq), mult(snd(map_L(head(v_bv))),head(v_fc))), add(thd(ineq), mult(thd(map_L(head(v_bv))),head(v_fc)))))
        else:
            return check(tail(v_bv), tail(v_fc), make_ineq(fst(map_L(head(v_bv))), add(snd(ineq), mult(snd(map_L(head(v_bv))),head(v_fc))), add(thd(ineq), mult(thd(map_L(head(v_bv))),head(v_fc)))))

def conflict(ineq):
    if fst(ineq) == "<":
        return not(0 < value(thd(ineq)))
    else:
        return not(0 <= value(thd(ineq)))

def checkProof():
    proofValid = True
    for i in conflict_list:
        proofValid = proofValid and conflict(check(i[0], i[1], ineq_in))
    return proofValid

###########################

ineq_in = make_ineq("<=", dict(zip(["0"],[Fraction("0")])), dict(zip(["1"],[Fraction("0")]))) # initial inequality

print(checkProof())
