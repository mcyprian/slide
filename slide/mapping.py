import sys
import pprint


def map_vars(preds1, preds2, top_call1, top_call2):
    '''
    Maps ekvivalent variables in predicates
    '''

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

    print "Top call 1:"
    pprint.pprint(list_top_call1)
#    print "\nPreds 1:"
#    pprint.pprint(tuple_preds1)
#    print "\n Not equals1:"
#    print(ne1)
#    print "\nTop call 2:"
#    pprint.pprint(list_top_call2)
#    print "\nPreds 2:"
#    pprint.pprint(tuple_preds2)
#    print "\n Not equals2:"
#    print(ne2)
#
    top_call1[0].expand(preds1[top_call1[0].pred_name], top_call1[0].call)
    top_call2[0].expand(preds2[top_call2[0].pred_name], top_call2[0].call)
    print "\nTop call 1 after expansion:"
    pprint.pprint(top_call1[0].expanded_rules_tuple_form)
#    print "\nTop call 1 global equals {}".format(top_call1[0].global_equal)
#    print "\nTop call 2 after expansion:"
#    pprint.pprint(top_call2[0].expanded_rules_tuple_form)
#    print "\nTop call 2 global equals {}".format(top_call2[0].global_equal)

    top_call1[0].expand(preds1[top_call1[0].expanded_rules[1].calles[0][0]],
                               top_call1[0].expanded_rules[1].calles[0][1])

    del top_call1[0].expanded_rules[1].calles[0]

    print "\nTop call 1 after second expansion:"
    pprint.pprint(top_call1[0].expanded_rules_tuple_form)


    return (tuple_preds1, list_top_call1, tuple_preds2, list_top_call2)

