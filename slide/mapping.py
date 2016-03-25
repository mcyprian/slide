# Michal Cyprian
#
# Expansion and mapping
#
# distributed under GNU GPL license

import sys
import pprint
import itertools

from input import InputError
from predicate_structures import TopCall, Rule

class MatchException(BaseException):
    pass


class MappingData(object):
    """Simple class to store set of allocated nodes and node identifiers
    aliases.
    """
    def __init__(self, identical=None, allocated_nodes=None):
        if not isinstance(identical, list):
            identical = [mapping_data.identical]

        if not isinstance(allocated_nodes, set):
            allocated_nodes = set([allocated_nodes])

        self.identical = identical
        self.allocated_nodes = allocated_nodes

    def get_aliases(self, var):
        """Returns list of identifier aliases of node var"""
        identical_list = [var]
        for s in self.identical:
            if var in s:
                identical_list.append((s - {var}).pop())
        return identical_list



def print_calles(lhs, rhs, mapping_data):
    """Visualize content of LHS, RHS and mapping_data.identical identificators"""

    list_lhs = [call.expanded_rules_tuple_form for call in lhs] 
    list_rhs = [call.expanded_rules_tuple_form for call in rhs] 
    print("\n--------------------------------------------------------------------")
    print ("LHS:")
    pprint.pprint(list_lhs)
    print ("\nRHS:")
    pprint.pprint(list_rhs)
    print("identical {}".format(mapping_data.identical))
    print("--------------------------------------------------------------------")


def expand_sophisticated(src, dest, preds, mapping_data, msg):
    """Iterates over allocated nodes on src side and search for predicate call
    containing node in arguments. Expands chosen predicate and
    returns True on success, False otherwise
    """
    print(msg)
    for src_call in src:
        for src_rule in src_call.expanded_rules:
            if src_rule.alloc:
                for call in dest:
                    for index, dest_rule in enumerate(call.expanded_rules):
                        if dest_rule.calles:
                            for pred_call in dest_rule.calles:
                                # allocated node or node mapping_data.identical to allocated appears in args of call
                                if set(mapping_data.get_aliases(src_rule.alloc)) & set(pred_call[1]):
                                    print("Expanding {}".format(pred_call))
                                    call.expand(preds[dest_rule.calles[0][0]],
                                                           dest_rule.calles[0][1],
                                                           dest[0].expanded_rules[0])
                                    dest_rule.equal = dest_rule.not_equal = []
                                    if not dest_rule.alloc and not dest_rule.pointsto\
                                       and not dest_rule.equal and not dest_rule.not_equal:
                                        del call.expanded_rules[index]
                                        return True
                                    else:
                                        del dest_rule.calles[0]
                                        return True
    return False


def expand_leftmost(top_call, preds, msg):
    """Expands leftmost predicate call of top_call argument.
    Returns True on success, False if top_call doesn't contain
    predicate_calls.
    """
    print(msg)
    for call in top_call:
        for index, rule in enumerate(call.expanded_rules):
            if rule.calles:
                call.expand(preds[rule.calles[0][0]], rule.calles[0][1])
                if not rule.alloc and not rule.pointsto and not rule.equal and not rule.not_equal:
                        del call.expanded_rules[index]
                        return True
                else:
                    del rule.calles[0]
                    return True
    return False


def match_rule(to_map, rhs_call, mapping_data):
    """Search for rule in RHS matching to_map rule from LHS.
    Returns index of call and index of rule in call that matches.
    """
    match = False

    for call_index, call in enumerate(rhs_call):
        for rule_index, rule in enumerate(call.expanded_rules):
            if to_map.alloc in TopCall.top_level_vars and to_map.alloc == rule.alloc or\
                {to_map.alloc, rule.alloc} in mapping_data.identical:
                match = node_match(zip(to_map.pointsto, rule.pointsto), mapping_data, match)
                if match == True:
                    print("\nMatch rule: {} top_level {}".format(to_map.quadruple, TopCall.top_level_vars))
                    print("succeded {} {}".format(call_index, rule_index))
                    print("rule {}".format(rule.quadruple))
                    return (call_index, rule_index)
    print("\nMatch rule: {} top_level {}".format(to_map.quadruple, TopCall.top_level_vars))
    print("failed")
    return (False, False)            


def match_call(to_map, rhs_call, mapping_data):
    """Search for predicate call in RHS matching to_map call from LHS.
    Returns index of call and index of rule in call that matches.
    """
    print("\nMatch call: {}".format(to_map.quadruple))
    match = False

    for call_index, call in enumerate(rhs_call):
        for rule_index, rule in enumerate(call.expanded_rules):
            if not rule.calles:
                continue
            if to_map.calles[0][0] == rule.calles[0][0]: # There is a call of the same predicate
                match = node_match(zip(to_map.calles[0][1], rule.calles[0][1]), mapping_data, match)
                if match == True:
                    print("succeded {} {}".format(call_index, rule_index))
                    return (call_index, rule_index)
    print("failed")
    return (False, False)            


def node_match(zip_object, mapping_data, match):
    """Iterates over zip_object containing doubles of nodes,
    checks if it is possible to map them.
    """
    for var_lhs, var_rhs  in zip_object:
        if var_lhs in TopCall.top_level_vars and var_lhs == var_rhs or\
                {var_rhs, var_lhs} in mapping_data.identical or var_rhs == 'nil' and var_lhs == 'nil':
            match = True
        elif var_rhs not in TopCall.top_level_vars and  var_rhs != 'nil':
            mapping_data.identical.append({var_rhs, var_lhs})
            match = True
        else:
            match = False
            break
    return match


def try_to_match_not_equals(to_map, lhs_call, mapping_data):
    """Search for not_equal in RHS matching to_map call from LHS.
    Returns index of call and index of rule in call that matches.
    """
    print("\nMatch not_equal: {}".format(to_map.quintuple))
    match = False

    for call in lhs_call:
        for rule in call.expanded_rules:
            if not rule.not_equal:
                continue
                
            for double in itertools.product(to_map.not_equal, rule.not_equal):
                # creates set of mapping_data.identical identifiers for each of variables in double:
                # (('to_map1', 'to_map2'), ('rule1', 'rule2'))
                print("DOUBLE {}".format(double))
                first_set_to_map = set(mapping_data.get_aliases(double[0][0]))
                second_set_to_map = set(mapping_data.get_aliases(double[0][1]))
                first_set_rhs = set(mapping_data.get_aliases(double[1][0]))
                second_set_rhs = set(mapping_data.get_aliases(double[1][1]))
                # if intersection of first two sets and second two sets exists,
                # we can match not equals 
                if first_set_to_map & first_set_rhs and second_set_to_map & second_set_rhs:
                    print("succeded {}".format(double))
                    for index, ne in enumerate(to_map.not_equal):
                        if ne == double[0]:
                            print("Removing {}".format(ne))
                            del to_map.not_equal[index]
                            break
                   # for index, ne in enumerate(rule.not_equal):
                   #     if ne == double[1]:
                   #         print("Removing {}".format(ne))
                   #         del rule.not_equal[index]
                   #         break
                    raise MatchException
    print("failed")

def try_to_match_equals(to_map, lhs_call, mapping_data):
    """Search for equal in RHS matching to_map call from LHS.
    Returns index of call and index of rule in call that matches.
    """
    print("\nMatch equal: {}".format(to_map.quintuple))
    match = False

    for call in lhs_call:
        for rule in call.expanded_rules:
            if not rule.equal:
                continue
                
            for double in itertools.product(to_map.equal, rule.equal):
                # creates set of mapping_data.identical identifiers for each of variables in double:
                # (('to_map1', 'to_map2'), ('rule1', 'rule2'))
                print("DOUBLE {}".format(double))
                first_set_to_map = set(mapping_data.get_aliases(double[0][0]))
                second_set_to_map = set(mapping_data.get_aliases(double[0][1]))
                first_set_rhs = set(mapping_data.get_aliases(double[1][0]))
                second_set_rhs = set(mapping_data.get_aliases(double[1][1]))
                # if intersection of first two sets and second two sets exists,
                # we can match not equals 
                if first_set_to_map & first_set_rhs and second_set_to_map & second_set_rhs:
                    print("succeded {}".format(double))
                    for index, ne in enumerate(to_map.equal):
                        if ne == double[0]:
                            print("Removing {}".format(ne))
                            del to_map.equal[index]
                            break
                   # for index, ne in enumerate(rule.equal):
                   #     if ne == double[1]:
                   #         print("Removing {}".format(ne))
                   #         del rule.equal[index]
                   #         break
                    raise MatchException
    print("failed")



def try_to_match_rule(lhs, index, rule, rhs, mapping_data):
    """Removes mapped parts of LHS, RHS if match_rule succeeded."""
    call_index, rule_index = match_rule(rule, rhs, mapping_data)
    if not isinstance(call_index, bool):
        del lhs[index]
        # Appends implicit not equals to lhs after pontsto match
        print("Adding implict not equal {}".format([(rule.alloc, node) for node in rule.pointsto]))
        lhs.append(TopCall())
        lhs[-1].expanded_rules.append(Rule('', [], [], [], [(rule.alloc, node) for node in rule.pointsto]))

        # Remove all other disjunctive parts of call
        rhs[call_index].expanded_rules = [rhs[call_index].expanded_rules[rule_index]]

        rule = rhs[call_index].expanded_rules[0]
        rule.alloc = ''
        rule.pointsto = []
        if not rule.alloc and not rule.pointsto and not rule.equal and not rule.not_equal and not rule.calles:
            del rhs[call_index].expanded_rules[0]
        raise MatchException


def try_to_match_call(lhs, index, rule, rhs, mapping_data):
    """Removes mapped parts of LHS, RHS if match_call succeeded."""
    call_index, rule_index =  match_call(rule, rhs, mapping_data)
    if not isinstance(call_index, bool):
        del lhs[index]

        # Remove all other disjunctive parts of call
        rhs[call_index].expanded_rules = [rhs[call_index].expanded_rules[rule_index]]

        rule = rhs[call_index].expanded_rules[0]
        rhs[call_index].expanded_rules[0].calles = None
        if not rule.alloc and not rule.pointsto and not rule.equal and not rule.not_equal and not rule.calles:
            del rhs[call_index]
        raise MatchException

def has_nodes(side_call):
    """Indicates if side_call argument contains any pointsto or predicate calls
    Returns: True if side_call consists only of equals and not_equals
             False if something else is present.
    """
    empty = False
    for call in side_call:
        for rule in call.expanded_rules:
            if rule.alloc or rule.pointsto or rule.calles:
                empty = True

    return empty

def is_empty(side_call):
    """Indicates if side_call is completely empty (everything was mapped) or
    not.
    """
    print([call.tuple_form for call in side_call])
    return [call.tuple_form for call in side_call]

def map_nodes(preds1, preds2, lhs, rhs):
    """Expanding predicate calles on LHS and RHS and tries to map parts of
    formulas to each other.
    """
    mapping_data = MappingData([], set())
    # Creating tuple forms of predicates
    tuple_preds1 = {}
    tuple_preds2 = {}
    list_lhs = [call.tuple_form for call in lhs] 
    list_rhs = [call.tuple_form for call in rhs] 

    ne1 = []
    ne2 = []

    for key in preds1:
        tuple_preds1[key] = preds1[key].short_tuple_form
        for rule in preds1[key].rules:
            ne1.append(rule.not_equal)

    for key in preds2:
        tuple_preds2[key] = preds2[key].short_tuple_form
        for rule in preds2[key].rules:
            ne2.append(rule.not_equal)

#    for n1, n2 in  zip(ne1, ne2):
#        if n1 or n2:
#            raise InputError("only disequalities of the for alloc!=nil are allowed")

    if len(lhs) == 1 and len(rhs) == 1:
        return (tuple_preds1, list_lhs, tuple_preds2, list_rhs)

    long_preds = {}

    for key in preds1:
        long_preds[key] = preds1[key].tuple_form

    print ("Preds:")
    pprint.pprint(long_preds)
    print_calles(lhs, rhs, mapping_data)
    
    num = 0
    while has_nodes(lhs) and has_nodes(rhs):
        try:
            for call_index, call in enumerate(lhs):
                if len(call.expanded_rules) > 1:
                    raise InputError("Disjunction on LHS, not implemented\n")
                rule = call.expanded_rules[0]
                try_to_match_rule(lhs, call_index, rule, rhs, mapping_data)
                if rule.calles:
                    try_to_match_call(lhs, call_index, rule, rhs, mapping_data)
        except MatchException:
            print("Successfull match, iteration restarted")
            print_calles(lhs, rhs, mapping_data)
        else:           
            result = expand_sophisticated(lhs, rhs, preds1, mapping_data, "Sophisticated expansion rhs") or\
            expand_sophisticated(rhs, lhs, preds1, mapping_data, "Sophisticated expansion lhs")
            if not result and num % 2 == 0:
                result = expand_leftmost(lhs, preds1, "Leftmost expansion lhs")
            elif not result:
                result = expand_leftmost(rhs, preds1, "Leftmost expansion rhs")
                
            num += 1
            print_calles(lhs, rhs, mapping_data)
            if num > 100:
                return (False, False, False, False)

    print("Start matching of not_equal")
    result = expand_leftmost(rhs, preds1, "Leftmost expansion rhs")
# ak je na pravo predikat
    while is_empty(rhs):
        for call in rhs:
            print_calles(lhs, rhs, mapping_data)
            rule = call.expanded_rules[0]
            try:
                try_to_match_equals(rule, lhs, mapping_data)
                try_to_match_not_equals(rule, lhs, mapping_data)
            except MatchException:
                continue
            else:
                num += 1
            if num > 100:
                return (False, False, False, False)

    return (True, True, True, True)
