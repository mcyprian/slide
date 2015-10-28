#!/usr/bin/python
#
# Adam Rogalewicz
# 
# SL to TA - entailment on empty heaps
# distrubuted under GNU GPL licence


def entailment(eh1,eh2):
    if eh1==[]:
        #False => everything
        return 1
    if [] in eh2:
        # everything => True
        return 1
    if eh2==[]:
        # something => False
        return 0
    print "-----------------------------------"
    print "WARNING: check empty heap inlcusion"
    print "LHS: ",eh1
    print "RHS: ",eh2
    print "Manual check needed"
    print "-----------------------------------"

    return 1
