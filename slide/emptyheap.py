#!/usr/bin/python3
#
# Adam Rogalewicz
# 
# SL to TA - entailment on empty heaps
# distrubuted under GNU GPL licence

# eq1 => eq2
# eq1 - a list of equal variables
# eq2 - a list of equal variables
def match(eq1,eq2):
    for x in eq2:
        if not x in eq1:
            return 0
    return 1


def entailment(lhs,rhs):
    # for each disjunct on LHS we must find a disjunct on RHS
    for disjleft in lhs:
        if rhs==[]:
            # something => False
            return 0
        for disjright in rhs:
            # for each equality on lhs:
            for eq1 in disjleft:
                tt=0
                for eq2 in disjright:
                    if match(eq1,eq2):
                        tt=1
                        break
                if not tt:
                    # eq1 on lhs not matched on rhs
                    return 0
    # everything matched
    return 1
