#!/usr/bin/python
#
# Adam Rogalewicz
# 
# SL to TA - top level calls
# distrubuted under GNU GPL licence

# use python entailment.py file_with_pred1 file_with_pred2

import input
import rotate
import sys
import os
import vata
import functions
import mapping
from settings import *
import emptyheap
import subprocess


def main(file_lhs,file_rhs,verbose):
    tiles=[]
    # first collect the free variables, which appear on both sides of the entailment
    if implicit_exists:
        free_lhs=input.get_free_variables(file_lhs)
        free_rhs=input.get_free_variables(file_rhs)
        if free_lhs=="ALL":
            if verbose:
                print "WARNING: LHS in the old format -> implicit quantification skiped"
            free="ALL"
        elif free_rhs=="ALL":
            if verbose:
                print "WARNING: RHS in the old format - implicit quantification skiped"
            free="ALL"
        else:
            free=[]
            for x in free_lhs:
                if x in free_rhs:
                    free.append(x)
    else:        
        free="ALL"
    # parse the input and create automata
    (preds1, top_call1, params1, root_rule1, empty_rule1) = input.parse_input(file_lhs, free) 
    (preds2, top_call2, params2, root_rule2, empty_rule2) = input.parse_input(file_rhs, free) 


    print("top call {}".format(top_call1))
    #TODO: Try to map predicates to each other
    m = mapping.map_vars(preds1, preds2, top_call1, top_call2)
    
    (aut1,emptyheap_eq1,eq_edges1)=input.make_aut(preds1, top_call1, params1, 
                                                  root_rule1, empty_rule1, tiles)
    (aut2,emptyheap_eq2,eq_edges2)=input.make_aut(preds2, top_call2, params2,
                                                  root_rule2, empty_rule2, tiles)
    # check entailment of empty heaps
    if not emptyheap.entailment(emptyheap_eq1,emptyheap_eq2):
        # no need to call all the machinery. Just UNSAT
        if verbose:
            print "Entailment result:"
        print "INVALID"
        return 0
    # compute rotation closure and check entailment 
    aut2_closure=rotate.rotate_closure(aut2,tiles)
    file1=functions.get_tmp_filename()
    file2=functions.get_tmp_filename()
    vata.aut_to_file(aut1,file1,"aut1")
    vata.call_vata_union(aut2_closure,file2)
    #print automata statistics in verbose mode
    if verbose:
        print "Number of states/transitions of A1: ",len(rotate.get_states(aut1)),"/", len(aut1["rules"])
        print "Number of states/transitions of A2 (before rot. closure): ",len(rotate.get_states(aut2)),"/",len(aut2["rules"])
        print "Number of states/transitions after closure of A2: ",len(vata.get_states_vata(file2)),"/",vata.get_trans_number(file2)
        print "Entailment result:"
    # call vata to check entailment
    result = subprocess.check_output("%s incl %s %s"%(VATA_path,file1,file2), shell=True)
    if result=="1\n":
        print "VALID"
    elif result=="0\n":
        if verbose and (eq_edges1 or eq_edges2):
            print "INVALID (equality edges in use => not COMPLETE answer)"
        elif (eq_edges1 or eq_edges2):
            print "UNKNOWN"
        else:
            print "INVALID"
    else:
        print "ERROR: %s us not a vata executable"
    # remove tmp files
    os.unlink(file1)
    os.unlink(file2)

# main call
if len(sys.argv)<3:
    print "Expected usage:"
    print "Standard mode (all error messages are provided): entailment.py file_with_pred1 file_with_pred2"
    print "Silent mode (no error messages): entailment.py -s file_with_pred1 file_with_pred2"
    sys.exit()
if sys.argv[1]=="-s":
    try:
        main(sys.argv[2],sys.argv[3],False)
    except:
        print "UNKNOWN"
        sys.exit(1)
else:
    main(sys.argv[1],sys.argv[2],True)
