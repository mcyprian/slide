import sys
import pprint

from input import InputError
from predicate_structures import TopCall

def print_calles(lhs, rhs):
    ne1 = []
    ne2 = []

    for call in lhs:
        for rule in call.expanded_rules:
            ne1.append(rule.not_equal)

    for call in rhs:
        for rule in call.expanded_rules:
            ne2.append(rule.not_equal)

    list_lhs = [call.tuple_form for call in lhs] 
    list_rhs = [call.tuple_form for call in rhs] 
    print ("\nLHS:")
    pprint.pprint(list_lhs)
    print("lhs not_equal {}".format(ne1))
    print ("\nRHS:")
    pprint.pprint(list_rhs)
    print("rhs not_equal {}".format(ne2))


def expand_next(top_call, preds):
    for call in top_call:
        for index, rule in enumerate(call.expanded_rules):
            if rule.calles:
                call.expand(preds[rule.calles[0][0]], rule.calles[0][1])
                if not rule.alloc and not rule.pointsto and not rule.equal and not rule.not_equal:
                        del call.expanded_rules[index]
                        return
                else:
                    del rule.calles[0]
                    return


def match_rule(to_map, rhs_call, identical):
    match = False

    for call_index, call in enumerate(rhs_call):
        for rule_index, rule in enumerate(call.expanded_rules):
            if to_map.alloc in TopCall.top_level_vars and to_map.alloc == rule.alloc or\
                {to_map.alloc, rule.alloc} in identical:
                for var_lhs, var_rhs  in zip(to_map.pointsto, rule.pointsto):
                    if var_lhs in TopCall.top_level_vars and var_lhs == var_rhs or\
                        var_rhs == 'nil' and var_lhs == 'nil':
                        match = True
                    elif var_rhs not in TopCall.top_level_vars and var_lhs != to_map.alloc and var_rhs != 'nil':
                        identical.append({var_rhs, var_lhs})
                        match = True
                    else:
                        match = False
                        break
                if match == True:
                    print("\nMatch rule: {} top_level {}".format(to_map.quadruple, TopCall.top_level_vars))
                    print("succeded {} {}".format(call_index, rule_index))
                    print("rule {}".format(rule.quadruple))
                    return (call_index, rule_index)
    print("\nMatch rule: {} top_level {}".format(to_map.quadruple, TopCall.top_level_vars))
    print("failed")
    return (False, False)            


def match_call(to_map, rhs_call, identical):
    print("\nMatch call: {}".format(to_map.quadruple))
    match = False

    for call_index, call in enumerate(rhs_call):
        for rule_index, rule in enumerate(call.expanded_rules):
            print("rule {}".format(rule.quadruple))
            if not rule.calles:
                continue
            if to_map.calles[0][0] == rule.calles[0][0]:
                for var_lhs, var_rhs  in zip(to_map.calles[0][1], rule.calles[0][1]):
                    if var_lhs in TopCall.top_level_vars and var_lhs == var_rhs or\
                            var_rhs == 'nil' and var_lhs == 'nil':
                        match = True
                    elif var_rhs not in TopCall.top_level_vars and  var_rhs != 'nil':
                        identical.append({var_rhs, var_lhs})
                        match = True
                    else:
                        match = False
                        break
                if match == True:
                    print("succeded {} {}".format(call_index, rule_index))
                    return (call_index, rule_index)
    print("failed")
    return (False, False)            


def try_to_match_rule(lhs, index, rule, rhs, identical):
    call_index, rule_index = match_rule(rule, rhs, identical)
    if not isinstance(call_index, bool):
        del lhs[index]
        rule = rhs[call_index].expanded_rules[rule_index]
        rule.alloc = ''
        rule.pointsto = []
        if not rule.alloc and not rule.pointsto and not rule.equal and not rule.not_equal and not rule.calles:
            del rhs[call_index].expanded_rules[rule_index]


def try_to_match_call(lhs, index, rule, rhs, identical):
    call_index, rule_index =  match_call(rule, rhs, identical)
    if not isinstance(call_index, bool):
        del lhs[index]
        rule = rhs[call_index].expanded_rules[rule_index]
        rhs[call_index].expanded_rules[rule_index].calles = None
        if not rule.alloc and not rule.pointsto and not rule.equal and not rule.not_equal and not rule.calles:
            del rhs[call_index].expanded_rules[rule_index]


def map_nodes(preds1, preds2, lhs, rhs):
    '''
    Tries to map ekvivalent variables in predicates
    '''
    identical = []
    # Creating tuple forms of predicates
    tuple_preds1 = {}
    tuple_preds2 = {}
    list_lhs = [call.tuple_form for call in lhs] 
    list_rhs = [call.tuple_form for call in rhs] 

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

#    for n1, n2 in  zip(ne1, ne2):
#        if n1 or n2:
#            raise InputError("only disequalities of the for alloc!=nil are allowed")

    if len(lhs) == 1 and len(rhs) == 1:
        return (tuple_preds1, list_lhs, tuple_preds2, list_rhs)

    print ("Top call 1:")
    pprint.pprint(list_lhs)
    print ("\nPreds 1:")
    pprint.pprint(tuple_preds1)
    print ("\n Not equals1:")
    print(ne1)
    print ("\nTop call 2:")
    pprint.pprint(list_rhs)
    print ("\nPreds 2:")
    pprint.pprint(tuple_preds2)
    print ("\n Not equals2:")
    print(ne2)


    num = 0
    while [call.tuple_form for call in lhs]:
        if num % 2 == 0:
            print("Expanding LHS")
            expand_next(lhs, preds1)
        else:
            print("Expanding RHS")
            expand_next(rhs, preds2)
    
        for call_index, call in enumerate(lhs):
            for rule in call.expanded_rules:
                try_to_match_rule(lhs, call_index, rule, rhs, identical)
                if rule.calles:
                    try_to_match_call(lhs, call_index, rule, rhs, identical)
        
        num += 1
        print_calles(lhs, rhs)
        if num > 100:
            return (False, False, False, False)

    return (True, True, True, True)
