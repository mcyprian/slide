"""Adam Rogalewicz

SL to TA
Utils of join operator on system of predicates

distrubuted under GNU GPL licence
"""

import re


class JoinFailed(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def create_intersection(a, b):
        # create list as an intersection between lists
    return [val for val in a if val in b]


def intersect_lists(a, b):
    # check intersection between the lists a and b
    # return the number of elements in the intersection
    number = 0
    for x in a:
        if x in b:
            number = number + 1
    return number


def get_list_position(item, l):
    if not item in l:
        l.append(item)
    return l.index(item)


def deleteandadd_call_item(prop_item, v_num, params_to_add, calls, to_remove):
    (p_name, params) = calls[prop_item]
    mod_params = list(params)  # make a fresh copy
    if to_remove:
        mod_params.pop(v_num)
        mod_params.extend(list(params_to_add))
        calls[prop_item] = (p_name, mod_params)
        return calls


def change_call_item_pred(prop_item, prefix, v_num, calls, tp_item):
    p_name, params = calls[prop_item]
    calls[prop_item] = ("%sx%sx%ix%i" % (prefix, p_name, v_num, tp_item), params)
    return calls


def add_on_position(l, pos, item):
    if pos == len(l):
        return list(l) + [item]
    if pos > len(l):
        raise JoinFailed("ERROR: This line should be not accessed")
    res = []
    for i in range(len(l)):
        if i == pos:
            res.append(item)
        res.append(l[i])
    return res


def alloc(pr, param_no, preds):
    # check whether the (param_no)^th parameter of the predicate "pr" is
    # allocated in all its rules
    (params, rules) = preds[pr]
    res = 1
    for (al, pt, calls, equal) in rules:
        if not (params[param_no] in [al] + equal):
            res = 0
    return res


def join_empty_heaps(empty1, empty2, candidate, to_remove):
    join = []
    # first join the emptyheap equalities
    for disj1 in empty1:
        for disj2 in empty2:
            aux = list(disj1) + list(disj2)
            aux = process_input.join_equalities(aux)
            aux2 = []
            for i in aux:
                aux2.append(process_input.remove_multiple_occurences(i))
            join.append(aux2)
    # remove candidate if "to_remove" is set
    if to_remove:
        join2 = []
        for disj in join:
            disj2 = []
            for i in disj:
                if candidate in i:
                    i.pop(i.index(candidate))
                    if not len(i) == 1:
                        disj2.append(i)
                else:
                    disj2.append(i)
            join2.append(disj2)
        join = join2
    return join


def apply_maps(v, map1, map2, forbid, only_first):
    # firstly apply mapping map1
    if not (v in map1.keys()):
        # create a fresh variable such that it is no in map[12].values() and forbid
        candidate = v
        while (candidate in map1.values()) or (candidate in map2.values()) or (candidate in forbid):
            candidate = candidate + "X"
        map1[v] = candidate
    if only_first:
        return map1[v]
    step1 = map1[v]
    # secondly apply mapping map2
    if not step1 in map2.keys():
        return step1
    return map2[step1]


def join_empty_LHS(call, params, new_call2, new_params2, old_call2, old_params2, preds, empty2):
    # RHS: call + params
    # new top call: new_call2 + new_params2
    #
    # first we find a mapping of internal parameters from the predicate "call"
    # to the internal parameters of the predicate "new_call2"
    # * internal call parameter (preds[call][0]) -> top level params (params)
    #   -> new top level params (new_params2) -> internal new top call parameter (preds[new_call2][0])
    # * internal parameter from the call equal to nil are translated into "nil-Xn" internal parameters of the new call
    call_p_map = {}
    nil_pos = 1
    for i in range(len(preds[call][0])):
        if params[i] == "nil":
            call_p_map[preds[call][0][i]] = "nil-X%i" % nil_pos
            if not ("nil-X%i" % nil_pos in preds[new_call2][0]):
                raise JoinFailed("JOIN: ERROR: this line should not be accesible")
            nil_pos = nil_pos + 1
        elif params[i] in new_params2:
            call_p_map[preds[call][0][i]] = preds[new_call2][0][new_params2.index(params[i])]
        elif params[i] in old_params2:
            # handle the param on which the join is applied if "to_remove was true"
            # (-->this param is not part of new_params2)
            call_p_map[preds[call][0][i]] = preds[old_call2][0][old_params2.index(params[i])]
        else:
            raise JoinFailed("JOIN: ERROR: this line should not be accesible")
    # map the empty2 inside the rule.
    if not len(empty2) == 1:
        raise JoinFailed("JOIN: not implemented")
    # we suppose that the equality  contains only a single disjunct
    # the other situation is not implemented
    disj = empty2[0]
    equal = []
    for conj in disj:
        new_conj = []
        for x in conj:
            new_conj.append(preds[old_call2][0][old_params2.index(x)])
            if x == "nil":
                new_conj.append("nil")
        equal.append(new_conj)
    equal1 = []
    for x in equal:
        equal1.append(process_input.remove_multiple_occurences(x))
    equal1 = process_input.join_equalities(equal1)
    new_rule_params = preds[new_call2][0]
    # in the forbid variable, we store parameters, which are checked for the following:
    # they must be existentially quantified
    # they must be used only in call and call2
    forbid = []
    # for each rule create a new rule
    new_rules = []
    for (al, pt, cls, eq) in preds[call][1]:
        # the system of predicates must be forward connected, so call_p_map[al] must be defined ...
        alloc = call_p_map[al]
        # find representatives
        mapping = {}
        for conj in equal1:
            if alloc in conj:
                repres = alloc
            else:
                tmp = intersect_lists(new_rule_params, conj)
                if tmp > 1:
                    # equality between formal parameters implemented only if they are equal to
                    # the allocated node
                    if "nil" in conj:
                        for x in conj:
                            if x == "nil":
                                pass
                            else:
                                if new_params2[new_rule_params.index(x)] == "nil":
                                    repres = x
                                else:
                                    # add to the forbid
                                    to_forbid = new_params2[new_rule_params.index(x)]
                                    if not (to_forbid in forbid):
                                        forbid.append(to_forbid)
                    else:
                        raise JoinFailed("JOIN: not implemented")
                elif tmp == 1:
                    for p in new_rule_params:
                        if p in conj:
                            repres = dp
                else:
                    repres = conj[0]
            for x in conj:
                mapping[x] = repres
        # the original rule is translated as folows:
        # first all variables are translated according to the "all_p_map"
        # every variable outside all_p_map is translated to an unique new name
        # second all variables are translated according to the "mapping"
        new_al = apply_maps(al, call_p_map, mapping, new_params2, 0)
        new_pt = []
        for x in pt:
            new_pt.append(apply_maps(x, call_p_map, mapping, new_params2, 0))
        new_cls = []
        for (call_pred, call_par) in cls:
            new_call_par = []
            for x in call_par:
                new_call_par.append(apply_maps(x, call_p_map, mapping, new_params2, 0))
            new_cls.append((call_pred, new_call_par))
        new_eq = []
        for x in eq:
            new_eq.append(apply_maps(x, call_p_map, mapping, new_params2, 1))
        for x in mapping.keys():
            if mapping[x] == new_al and (not x in new_eq):
                new_eq.append(x)
        # pop alocated node fron the equality list - not needed
        if new_al in new_eq:
            new_eq.pop(new_eq.index(new_al))
        new_rules.append((new_al, new_pt, new_cls, new_eq))
    # add the newly created rules inside preds
    par, rules = preds[new_call2]
    rules = rules + new_rules
    preds[new_call2] = (par, rules)
    return forbid


def do_join(candidate, call, params, empty1, call2, params2,
            empty2, preds, par_intersect, to_remove):
    # LHS: call2,params2,empty2
    # RHS: call,params,empty1

    pos = process_input.get_param_numbers(params, candidate)
    if not len(pos) == 1:
        raise JoinFailed("JOIN: Not implemented")
    params_prop = list(params)
    params_prop.pop(pos[0])
    # parameters equal to nil must get canonical names.
    nilnum = 1
    for i in range(len(params_prop)):
        if "nil-X" in params_prop[i]:
            raise JoinFailed("JOIN: Name %s is forbiden in the input file" % params_prop[i])
        if params_prop[i] == "nil":
            params_prop[i] = "nil-X%i" % nilnum
            nilnum = nilnum + 1
    # check for the forbiden names in the params2
    for name in params2:
        if "nil-X" in name:
            raise JoinFailed("JOIN: Name %s is forbiden in the input file" % name)

    # this guarantee that params_prop are not used within the system of predicates
    process_input.rename_conflicts_with_params(preds, params_prop)
    # remove the parameters in the intersection between params and params2
    # different from candidate from params_prop
    params_prop_orig = list(params_prop)  # make a copy
    tracked_params_RHS = []
    tracked_params_LHS = []
    for p in par_intersect:
        tracked_params_RHS.append(params_prop.index(p))
        tracked_params_LHS.append(params2.index(p))
    for p in par_intersect:
        params_prop.pop(params_prop.index(p))
    tracked_params = [tracked_params_LHS]

    new_params2 = list(params2) + list(params_prop)
    # if candidate is existentially quantified, the it is not needed in the parameters any more
    if to_remove:
        new_params2.pop(params2.index(candidate))
    # rename all nil-X in new_params2 back to nil
    for i in range(len(new_params2)):
        if re.search("^nil-X", new_params2[i]):
            new_params2[i] = "nil"
    # we have to track the parameter z from call2 and attach the call to the
    # place, where z is reffered
    prefix = candidate
    while process_input.unique_pred_prefix(preds, prefix) == 0:
        prefix = prefix + "X"
    TODO = [(call2, params2.index(candidate), 0)]
    DONE = []
    new_call2 = "%sx%sx%ix0" % (prefix, call2, params2.index(candidate))
    while len(TODO):
        (p_name, v_num, t_pars) = TODO.pop()
        DONE.append((p_name, v_num, t_pars))
        # create a set of new parameters
        new_params = list(preds[p_name][0]) + list(params_prop)
        if to_remove:
            var_name = new_params.pop(v_num)
        else:
            var_name = new_params[v_num]
        # get names for the tracked parameters
        t_pars_local = []
        for p in tracked_params[t_pars]:
            t_pars_local.append(new_params[p])
        # for all rules of the given predicate
        new_rules = []
        for (alloc, pointsto, calls, equal) in preds[p_name][1]:
            if var_name == alloc or var_name in equal:
                # variable allocated - no join possible
                raise JoinFailed("Join ERROR: variable allocated")
            elif var_name in pointsto:
                (prop_pred, prop_item, prop_num) = process_input.propagated(var_name, calls)
                if prop_num == -1:
                    # create a set of parameters according to params_prop_orig and t_pars_local
                    pars = list(params_prop_orig)
                    for i in range(len(tracked_params_RHS)):
                        pars[tracked_params_RHS[i]] = t_pars_local[i]
                    new_cls = list(calls)
                    new_pars = add_on_position(pars, pos[0], var_name)
                    new_cls.append((call, new_pars))
                    new_rules.append((alloc, pointsto, new_cls, equal))
                    # inline the empty rule inside
                    if not empty1 == []:
                        for disjunct in empty1:
                            # rename variables from disjunct to the local variables
                            # the mapping is given 1:1 by params -> new_pars
                            local_copy = []
                            for conj in disjunct:
                                new_conj = []
                                for x in conj:
                                    new_conj.append(new_pars[params.index(x)])
                                local_copy.append(new_conj)
                            tmp = process_input.create_new_rule(
                                alloc, pointsto, 0, equal, new_params, local_copy, calls)
                            new_rules.append(tmp)

                else:
                    raise JoinFailed(
                        "Join Error: variable %s refered and propagated in predicate %s" %
                        (candidate, p_name))
            else:
                # tady je treba prepocitat tracked_params
                (prop_pred, prop_item, prop_var_num) = process_input.propagated(var_name, calls)
                if prop_var_num >= 0:
                    new_calls = deleteandadd_call_item(
                        prop_item, prop_var_num, params_prop, list(calls), to_remove)
                    # compute, how the tracked_variables are progressed
                    t_vars_prop = []
                    for tv in t_pars_local:
                        tv_pred, tv_item, tv_var_num = process_input.propagated(tv, calls)
                        if not (tv_item == prop_item and prop_pred == tv_pred):
                            raise JoinFailed("JOIN: complicated join, not implemented")
                        t_vars_prop.append(tv_var_num)
                    tp_item = get_list_position(t_vars_prop, tracked_params)
                    # change the predicate name in the item "prop_item"
                    new_calls = change_call_item_pred(
                        prop_item, prefix, prop_var_num, new_calls, tp_item)

                    new_rules.append((alloc, pointsto, new_calls, equal))
                    if not(((prop_pred, prop_var_num, tp_item) in DONE)
                           or ((prop_pred, prop_var_num, tp_item) in TODO)):
                        TODO.append((prop_pred, prop_var_num, tp_item))
                else:
                    raise JoinFailed(
                        "ERROR: variable %s not propagated (or multiple propagated) from the rule %s" %
                        (candidate, p_name))

        # add the newly created predicate into a list of predicates
        preds["%sx%sx%ix%i" % (prefix, p_name, v_num, t_pars)] = (new_params, new_rules)

    # The case where LHS has empty heap is solved separatelly
    forbid = []
    new_empty = []
    if not empty2 == []:
        new_empty = join_empty_heaps(empty1, empty2, candidate, to_remove)
        forbid1 = join_empty_LHS(
            call,
            params,
            new_call2,
            new_params2,
            call2,
            params2,
            preds,
            empty2)
        # all "nil" should be removed from forbid
        for x in forbid1:
            if (not x == "nil"):
                forbid.append(x)
    return (new_call2, new_params2, new_empty, forbid)
