import sys

###########################

ptrefs = open("input.uf","r") # open file in read mode
uf_proofs = open("proof.ufTheory","r") # open file in read mode

terms = {}

def buildTerms():
    for line in ptrefs.readlines():
        split = line.split()
        assert len(split) >= 2
        termId = int(split[0])
        symbol = split[1]
        args = [int(arg) for arg in split[2:]]
        terms[termId] = (symbol, args)

def to_equality(eq_str):
    #print("to_equality called on " + eq_str)
    sides = eq_str.split(",")
    assert(len(sides)==2)
    lhs = int(sides[0].lstrip('['))
    rhs = int(sides[1].rstrip(']'))
    return (lhs,rhs)

def normalize_equality(eq): # we are using symmetry implicitly
    if (eq[0] > eq[1]):
        return (eq[1], eq[0])
    return eq

def to_normalized_equality(eq_str):
    return normalize_equality(to_equality(eq_str))

def get_congruence_premises(equality):
    lhs = equality[0]
    rhs = equality[1]
    lhs_def = terms[lhs]
    rhs_def = terms[rhs]
    assert lhs_def[0] == rhs_def[0] #symbols are same
    assert len(lhs_def[1]) == len(rhs_def[1])
    premises = zip(lhs_def[1], rhs_def[1])
    return [normalize_equality(eq) for eq in premises]

def check_same_symbol(t1, t2):
    return terms[t1][0] == terms[t2][0]

def check_derivation(equality, derivations, premises, already_checked):
    #print("Checking derivation: [{0},{1}]".format(equality[0], equality[1]))
    if equality[0] == equality[1]: #reflexivity
        return True
    if equality in already_checked: # cache to avoid repetitive checks
        return True
    if equality not in derivations:
        print("Error, the equality {0}={1} does not have derivation".format(equality[0], equality[1]))
        return False
    derivation = derivations[equality]
    #print(derivation)
    if derivation == 'p':
        return normalize_equality(equality) in premises
    if derivation == 'c':
        if not check_same_symbol(equality[0], equality[1]):
            return False
        congruence_premises = get_congruence_premises(equality)
        #print("Using congruence on " + " ".join([str(p) for p in congruence_premises]))
        res = all(check_derivation(premise, derivations, premises, already_checked) for premise in congruence_premises)
        if res:
            already_checked.add(equality)
        return res
    else:
        #transitivity
        obligations = [to_normalized_equality(obligation) for obligation in list(filter(None, derivation.split(' ')))]
        #print("Using transitivity on " + " ".join([str(p) for p in obligations]))
        if len(obligations) < 2:
            print("Error in checking a derivation by transitivity")
            return False
        res = all([check_derivation(obligation, derivations, premises, already_checked) for obligation in obligations])
        if res:
            already_checked.add(equality)
        return res

def parse_header(header_str):
    #print("Header: " + header_str)
    assert(header_str[0:2]) == '(h'
    fields = header_str.split()[1:]
    assert(len(fields) >= 1)
    obligation = to_normalized_equality(fields[0])
    premises = [to_normalized_equality(field) for field in fields[1:]]
    return (obligation, premises)

def checkSingleProof(proof_str):
    #print("Proof string: " + proof_str)
    derivations = {}
    lines = proof_str.split('\n')
    #print(lines)
    assert lines[-1] == ')'
    header = lines[0]
    #print(header)
    (obligation, premises) = parse_header(header)
    #print("Header: " + header)
    derivation_lines = lines[1:-1]
    # read derivations
    for derivation in derivation_lines:
        split = derivation.split(';')
        assert len(split)==2, 'missing semicolon in proof line'
        equality = to_normalized_equality(split[0])
        derivations[equality] = split[1]
    return check_derivation(obligation, derivations, premises, set())

def checkUFProofs():
    res = True
    proof_str = ''
    for line in uf_proofs.readlines():
        if line == '\n':
            continue
        proof_str += line
        if line == ')\n':
            res = checkSingleProof(proof_str.rstrip('\n'))
            proof_str = ''
            if not res:
                return False
    return res

buildTerms()
ptrefs.close()

print(checkUFProofs())
uf_proofs.close()
