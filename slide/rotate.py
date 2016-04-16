"""Adam Rogalewicz

SL to TA - rotation closure of canonically tiled tree automata labeled
distrubuted under GNU GPL licence
"""

import string

from slide import functions


class RotateError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def unique_prefix(states):
    pref = ""
    act = 0
    while True:
        good = 1
        for x in states:
            if x.find(pref + string.ascii_uppercase[act]) == 0:
                good = 0
                break
        if good:
            return pref + string.ascii_uppercase[act]
        if act < len(string.ascii_uppercase):
            act = act + 1
        else:
            act = 0
            pref = pref + "X"


def get_states(aut):
    states = [aut["fin"]]
    for (symbol, lhs, rhs) in aut["rules"]:
        if not(rhs in states):
            states = states + [rhs]
        for x in lhs:
            if not(x in states):
                states = states + [x]
    return states


def check_tile_forward_connectivity(tuple_arg):
    (a, b, c, d) = tuple_arg
    if len(a) == 1:
        return 1
    for i in range(1, len(a)):
        if a[i] == []:
            return 0
    return 1


def rotate_new_fin(tuple_arg, qfin, pref, tiles):
    (symbol, lhs, rhs) = tuple_arg
    (aa, b, c, d) = tiles[symbol]
    a = list(aa)  # !!!! call by value/call by name !!!! @#$%^%^&**(
    a.append(a[0])
    del a[0]
    lhs.append(pref + rhs)  # the output state "rhs" is changed to "pref+rhs" input state
    rhs = qfin  # a new outpust state of the rule
    (a, lhs) = functions.paralel_sort(a, lhs)
    a = [[]] + a
    new_tile = functions.tile_normalize((a, b, c, d))
    if check_tile_forward_connectivity(new_tile):
        symbol = functions.tile_index(new_tile, tiles)
        return((symbol, lhs, rhs))
    else:
        # TILE NOT connected
        return(())


def rotate_old_root(tuple_arg, lhs_num, pref, tiles):

    (symbol, lhs, rhs) = tuple_arg
    new_lhs = list(lhs)
    del new_lhs[lhs_num]
    tile_new_pt1 = list(tiles[symbol][0])
    tmp = tile_new_pt1.pop(lhs_num + 1)
    tile_new_pt1[0] = tmp
    new_tile = (tile_new_pt1, tiles[symbol][1], tiles[symbol][2], tiles[symbol][3])
    new_tile = functions.tile_normalize(new_tile)
    if check_tile_forward_connectivity(new_tile):
        symbol = functions.tile_index(new_tile, tiles)
        return((symbol, new_lhs, pref + lhs[lhs_num]))
    else:
        # TILE NOT connected
        return(())


def rotate_intermediate(tuple_arg, lhs_num, pref, tiles):
    (symbol, lhs, rhs) = tuple_arg
    new_lhs = list(lhs)
    del new_lhs[lhs_num]
    new_lhs.append(pref + rhs)
    tile_new_pt1 = list(tiles[symbol][0])
    tmp = tile_new_pt1.pop(lhs_num + 1)
    tile_new_pt1.append(tile_new_pt1[0])
    del tile_new_pt1[0]
    (tile_new_pt1, new_lhs) = functions.paralel_sort(tile_new_pt1, new_lhs)
    tile_new_pt1 = [tmp] + tile_new_pt1
    new_tile = (tile_new_pt1, tiles[symbol][1], tiles[symbol][2], tiles[symbol][3])
    new_tile = functions.tile_normalize(new_tile)
    if check_tile_forward_connectivity(new_tile):
        symbol = functions.tile_index(new_tile, tiles)
        return((symbol, new_lhs, pref + lhs[lhs_num]))
    else:
        # TILE NOT connected
        return(())


def rotate_closure(aut, tiles):
    # get states from the original automaton
    states = get_states(aut)
    # compute a set of states in the new automaton
    unique_pref = unique_prefix(states)
    new_states = []
    for x in states:
        new_states.append(x)
        new_states.append(unique_pref + x)
    # create a new final state
    qfin = unique_prefix(new_states) + 'newfin'
    # result will be a tuple of automata
    res = []
    # for each rule compute the rotation
    for (symbol, lhs, rhs) in aut['rules']:
        if rhs == aut['fin']:
            if not(tiles[symbol][0][0] == []):
                print(
                    rhs,
                    " is final state, but tile contains ",
                    tiles[symbol][0][0],
                    " in -1 part")
                raise RotateError("STOPED")
            res.append(aut)  # the result is the original automaton
            continue
        rule = rotate_new_fin((symbol, list(lhs), rhs), qfin, unique_pref, tiles)
        if rule == ():
            # forward conectivity is broken by rotation
            continue
        new_aut = {}
        new_aut['fin'] = qfin
        new_aut['rules'] = list(aut['rules'])  # make a fresh copy of the original rules
        new_aut['rules'].append(rule)
        res.append(new_aut)
        TODO = [rhs]
        DONE = []
        while not(TODO == []):
            q = TODO.pop(0)
            DONE.append(q)
            for (symbol1, lhs1, rhs1) in aut['rules']:  # for each state equal to q in lhs
                for x in range(0, len(lhs1)):
                    if not(lhs1[x] == q):
                        continue
                    if rhs1 == aut['fin']:
                        if not(tiles[symbol1][0][0] == []):
                            print(
                                rhs1,
                                " is final state, but tile contains ",
                                tiles[symbol1][0][0],
                                " in -1 part")
                            raise RotateError("STOPED")
                        rule = rotate_old_root((symbol1, list(lhs1), rhs1), x, unique_pref, tiles)
                        # if forward conectivity is broken by rotation, then do nothing
                        if not (rule == ()):
                            new_aut['rules'].append(rule)
                    else:
                        rule = rotate_intermediate(
                            (symbol1, list(lhs1), rhs1), x, unique_pref, tiles)
                        # if forward conectivity is broken by rotation, then do nothing
                        if not (rule == ()):
                            new_aut['rules'].append(rule)
                            if not (rhs1 in DONE):
                                DONE.append(rhs1)
                                TODO.append(rhs1)
    return res
