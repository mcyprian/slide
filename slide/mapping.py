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
    """Visualize content of LHS, RHS and identical identifiers"""
    print("\n--------------------------------------------------------------------")
    print ("LHS:")
    pprint.pprint(lhs.calls_tuple_form)
    print ("\nRHS:")
    pprint.pprint(rhs.calls_tuple_form)
    print("identical {}".format(mapping_data.identical))
    print("allocated_nodes {}".format(mapping_data.allocated_nodes))
    print("--------------------------------------------------------------------")


def expand_sophisticated(src, dest, preds, mapping_data, msg):
    """Iterates over allocated nodes on src side and search for predicate call
    containing node in arguments. Expands chosen predicate and
    returns True on success, False otherwise
    """
    print(msg)
    for src_rule in src:
        if src_rule.alloc:
            for dest_rule in dest:
                for pred_call in dest_rule.calles:
                    # allocated node or node identical to allocated appears in args of call
                    if set(mapping_data.get_aliases(src_rule.alloc)) & set(pred_call[1]):
                        print("Expanding {}".format(pred_call))
                        dest.expand_current_call(preds, dest[0].expanded_rules[0])
                        return True
    return False


def expand_leftmost(top_call, preds, msg):
    """Expands leftmost predicate call of top_call argument.
    Returns True on success, False if top_call doesn't contain
    predicate_calls.
    """
    print(msg)
    for rule in top_call:
        if rule.calles:
            top_call.expand_current_call(preds)
            return True
    return False


def match_rule(lhs, to_map, rhs_call, mapping_data):
    """Search for rule in RHS matching to_map rule from LHS.
    raises MatchException on success.
    """
    match = False

    for rule in rhs_call:
        if to_map.alloc in TopCall.top_level_vars and to_map.alloc == rule.alloc or\
            {to_map.alloc, rule.alloc} in mapping_data.identical:
            match = node_match(zip(to_map.pointsto, rule.pointsto), mapping_data, match)
            if match is True:
                print("\nMatch rule: {} top_level {}".format(to_map.quadruple, TopCall.top_level_vars))
                print("Succeded, rule {}".format(rule.quadruple))
                mapping_data.allocated_nodes |= {rule.alloc, to_map.alloc}
                rhs_call.del_current_rule(remove_disjunctive=True)
                # Disjunction on lhs is not allowed index 0 can be used
                lhs.empty_first_rule()
                raise MatchException
    print("\nMatch rule: {} top_level {}".format(to_map.quadruple, TopCall.top_level_vars))
    print("failed")


def match_call(lhs, to_map, rhs_call, mapping_data):
    """Search for predicate call in RHS matching to_map call from LHS,
    raises MatchException on success.
    """
    print("\nMatch call: {}".format(to_map.quadruple))
    match = False

    for rule in rhs_call:
        if not rule.calles:
            continue
        if to_map.calles[0][0] == rule.calles[0][0]: # There is a call of the same predicate
            match = node_match(zip(to_map.calles[0][1], rule.calles[0][1]), mapping_data, match)
            if match == True:
                print("Succeded, call {}".format(rule.calles))
                rule.calles = None
                rhs_call.del_current_rule(remove_disjunctive=True)
                lhs.empty_first_call()
                raise MatchException
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


def match_implicit_not_equals(rhs, mapping_data):
    """Finds implict not equals on rhs -> both nodes were allocated
    or one node was allocated and the other is nil
    """
    for rule in rhs:
        for index, ne in enumerate(rule.not_equal):
            if (len(set(ne) & mapping_data.allocated_nodes) == 2 or
                (len(set(ne) & mapping_data.allocated_nodes) == 1 and
                 'nil' in set(ne))):
                    print("Removing implicit not equal {}".format(ne))
                    del rule.not_equal[index]
                    return True
    return False


def match_not_equals(to_map, lhs_call, mapping_data):
    """Search for not_equal in RHS matching to_map call from LHS.
    Returns index of call and index of rule in call that matches.
    """
    print("\nMatch not_equal: {}".format(to_map.quintuple))
    match = False

    for rule in lhs_call:
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
                raise MatchException
    print("failed")


def equals_to_identical(rhs, mapping_data):
    """Moves all local = local, global = local equals to identical set
    """
    for rule in rhs:
        for eq in rule.equal:
            if len(set(TopCall.top_level_vars) & set(eq)) < 2:
                mapping_data.identical.append(set(eq))
                print("Moving {} to identical".format(eq))
                rhs.del_current_rule()
                return True
    return False
            

def map_nodes(preds1, preds2, lhs, rhs):
    """Expanding predicate calles on LHS and RHS and tries to map parts of
    formulas to each other.
    """
    # Raises exception if disjunction appears on lhs. 
    lhs.disjunction_check = True
    mapping_data = MappingData([], set())
    # Creating tuple forms of predicates
    tuple_preds1 = {}
    tuple_preds2 = {}

    for key in preds1:
        tuple_preds1[key] = preds1[key].short_tuple_form

    for key in preds2:
        tuple_preds2[key] = preds2[key].short_tuple_form

    if len(lhs) == 1 and len(rhs) == 1:
        return (tuple_preds1, lhs.calls_tuple_form, tuple_preds2, rhs.calls_tuple_form)

    long_preds = {}

    for key in preds1:
        long_preds[key] = preds1[key].tuple_form

    print ("Preds:")
    pprint.pprint(long_preds)
    print_calles(lhs, rhs, mapping_data)
    
    num = 0
    while lhs.has_nodes and rhs.has_nodes:
        try:
            for rule in lhs:
                match_rule(lhs, rule, rhs, mapping_data)
                if rule.calles:
                    match_call(lhs, rule, rhs, mapping_data)
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

    # One expansion of top call where is still a predicate call present.
    # If result of expansion is disjunction part of it containg nodes will be
    # removed 
    if lhs.has_nodes:
        expand_leftmost(lhs, preds1, "Leftmost expansion lhs")
        lhs.remove_nodes_from_disjunction
    elif rhs.has_nodes:
        expand_leftmost(rhs, preds1, "Leftmost expansion rhs")
        rhs.remove_nodes_from_disjunction

    while equals_to_identical(rhs, mapping_data):
        pass

    while match_implicit_not_equals(rhs, mapping_data):
        pass

    while rhs.is_empty:
        for rule in rhs:
            print_calles(lhs, rhs, mapping_data)
            try:
                match_not_equals(rule, lhs, mapping_data)
            except MatchException:
                rhs.empty_first_rule()
                continue
            else:
                num += 1
            if num > 100:
                return (False, False, False, False)

    return (True, True, True, True)
