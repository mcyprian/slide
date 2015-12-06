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

    for key in preds1:
        tuple_preds1[key] = preds1[key].tuple_form
    
    for key in preds2:
        tuple_preds2[key] = preds2[key].tuple_form

    print "Top call 1:"
    pprint.pprint(list_top_call1)
    print "\nPreds 1:"
    pprint.pprint(tuple_preds1)
    print "\nTop call 2:"
    pprint.pprint(list_top_call2)
    print "\nPreds 2:"
    pprint.pprint(tuple_preds2)

    top_call1[0].expand(preds1[top_call1[0].pred_name])
    top_call2[0].expand(preds2[top_call2[0].pred_name])
    print "\nTop call 1 after expansion:"
    pprint.pprint(top_call1[0].expanded_rules_tuple_form)
    print "\nTop call 2 after expansion:"
    pprint.pprint(top_call2[0].expanded_rules_tuple_form)
    sys.exit(1)
