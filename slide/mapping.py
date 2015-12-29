import sys
import pprint

from input import InputError

def expand_next(top_call, preds):
    for item in top_call:
        if not item.expanded_rules:
            item.expand(preds[item.pred_name], item.call)
            break

def map_vars(preds1, preds2, top_call1, top_call2):
    '''
    Tries to map ekvivalent variables in predicates
    '''

    # Creating tuple forms of predicates
    tuple_preds1 = {}
    tuple_preds2 = {}
    list_top_call1 = [call.tuple_form for call in top_call1] 
    list_top_call2 = [call.tuple_form for call in top_call2] 

    ne1 = []
    ne2 = []

    for key in preds1:
        tuple_preds1[key] = preds1[key].tuple_form
        for rule in preds1[key].rules:
            ne1.append(rule.not_equal)

    for key in preds2:
        tuple_preds2[key] = preds2[key].tuple_form
        for rule in preds2[key].rules:
            ne2.append(rule.not_equal)

    if len(top_call1) == 1 and len(top_call2) == 1:
        return (tuple_preds1, list_top_call1, tuple_preds2, list_top_call2)

    print "Top call 1:"
    pprint.pprint(list_top_call1)
    print "\nPreds 1:"
    pprint.pprint(tuple_preds1)
    print "\n Not equals1:"
    print(ne1)
    print "\nTop call 2:"
    pprint.pprint(list_top_call2)
    print "\nPreds 2:"
    pprint.pprint(tuple_preds2)
    print "\n Not equals2:"
    print(ne2)

    for n1, n2 in  zip(ne1, ne2):
        if n1 or n2:
            raise InputError("only disequalities of the for alloc!=nil are allowed")

    expand_next(top_call1, preds1)
    expand_next(top_call2, preds2)
    list_top_call1 = [call.tuple_form for call in top_call1] 
    list_top_call2 = [call.tuple_form for call in top_call2] 
    print "\nTop call 1 after expansion:"
    pprint.pprint(list_top_call1)
    print "\nTop call 2 after expansion:"
    pprint.pprint(list_top_call2)

    if len(top_call1) > len(top_call2):
        expand_next(top_call1, preds1)
        list_top_call1 = [call.tuple_form for call in top_call1] 
    else:
        expand_next(top_call2, preds1)
        list_top_call2 = [call.tuple_form for call in top_call2] 

    print "\nTop call 1 after expansion:"
    pprint.pprint(list_top_call1)
    print "\nTop call 2 after expansion:"
    pprint.pprint(list_top_call2)

#    top_call1[0].expand(preds1[top_call1[0].expanded_rules[1].calles[0][0]],
#                               top_call1[0].expanded_rules[1].calles[0][1])

#   del top_call1[0].expanded_rules[1].calles[0]

#    print "\nTop call 1 after second expansion:"
#    pprint.pprint(top_call1[0].expanded_rules_tuple_form)


    return (tuple_preds1, list_top_call1, tuple_preds2, list_top_call2)

