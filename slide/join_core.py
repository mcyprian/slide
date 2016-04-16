"""Adam Rogalewicz

 SL to TA
 Main function of join operator on system of predicates

 distrubuted under GNU GPL licence
 """

from slide.join_utils import intersect_lists, alloc


def join(preds, top_calls, emptyheap_eq, ex_quantified):
    # it emptyheap_eq==[] then join sould not create some empty heap - assert in the furure
    work_with_emptyheap = (not emptyheap_eq == [])
    while len(top_calls) > 1:
        # pick the first call for the join
        call, params = top_calls.pop(0)
        if emptyheap_eq == []:
            empty = []
        else:
            empty = emptyheap_eq.pop(0)
        # find a second call for a join
        # maximal number of attempts is given by the number of top calls
        candidate = ""
        count = 0
        while (candidate == "") and (count < len(top_calls)):
            count = count + 1
            find = 0
            for i in range(len(top_calls)):
                call2, params2 = top_calls[i]
                if emptyheap_eq == []:
                    empty2 = []
                else:
                    empty2 = emptyheap_eq[i]
                p_intersect = create_intersection(params, params2)
                if not (p_intersect == [] or (len(p_intersect) == 1 and "nil" in p_intersect)):
                    top_calls.pop(i)
                    if not emptyheap_eq == []:
                        emptyheap_eq.pop(i)
                    find = 1
                    break
            if find == 0:
                raise JoinFailed("Join failed")
            # find the candidate variable
            # - the candidate must be allocated in head of one of the calls
            # - the candidate must be an existentially quantified variable
            # - the candidate must be a link only between these two calls
            candidate = ""
            for par in p_intersect:
                if (alloc(call, params.index(par), preds)):
                    candidate = par
            if candidate == "":
                # swap positions of call and call2
                call_aux = call
                call = call2
                call2 = call_aux
                params_aux = params
                params = params2
                params2 = params_aux
                empty_aux = empty
                empty = empty2
                empty2 = empty_aux
                for par in p_intersect:
                    if (alloc(call, params.index(par), preds)):
                        candidate = par
            if candidate == "":
                # still no success,  push call (originally call2) back to topcalls
                # swap back call2 to call
                # then we will try so other item from topcall as call2
                top_calls.append((call, params))
                if work_with_emptyheap:
                    emptyheap_eq.append(empty)
                (call, params, empty) = (call2, params2, empty2)
        # check whether the candidate was found
        if candidate == "":
            raise JoinFailed(
                "Join failed: impossible to join the input into a single predicate call (or bad strategy)")
        if candidate == "nil":
            raise JoinFailed(
                "Something odd happened: nil taken as a candidate. nil existantially quantified in RootCall?")
        # create a list of other parameters (different from candidate and nil) shared between the two calls
        # pop the "candidate"
        p_intersect.pop(p_intersect.index(candidate))
        # pop all "nil" variables
        while "nil" in p_intersect:
            p_intersect.pop(p_intersect.index("nil"))

        # the candidate is removed from the parameters after join
        # if is it existentially quantified and it is not a parameter of other top level call
        to_remove = candidate in ex_quantified
        for (callX, paramsX) in top_calls:
            if candidate in paramsX:
                to_remove = False
                #raise JoinFailed("Join failed: parameter %s is in more the two calls on top level"%candidate)
        (call, params, empty, forbid) = do_join(candidate, call, params,
                                                empty, call2, params2, empty2, preds, p_intersect, to_remove)
        # check that variables in forbid are no more part of top calls and forbid
        # is ex_quantificated
        for x in forbid:
            if not x in ex_quantified:
                raise JoinFailed("JOIN: forbiden variable is not existentially quantified")
        for (c, p) in top_calls:
            if intersect_lists(p, forbid) > 0:
                raise JoinFailed("JOIN: forbiden variable in other calls")
        # add the newly created top call
        top_calls.append((call, params))
        if work_with_emptyheap:
            emptyheap_eq.append(empty)
        elif (not empty == []):
            raise JoinFailed("JOIN: ERROR: created emptyheap from some non-empty stuff")

    root_rule, root_params = top_calls[0]
    if emptyheap_eq == []:
        ret_empty = []
    else:
        ret_empty = emptyheap_eq[0]
    return (root_rule, root_params, ret_empty)
