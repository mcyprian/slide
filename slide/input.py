# Adam Rogalewicz
# 
# SL to TA
# distrubuted under GNU GPL licence

from predicate_structures import Rule, Predicate, TopCall, CallsContainer
import re
import functions
import join


class InputError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def remove_eol(x):
    return re.sub("\n","",x)

def remove_whitespaces(x):
    (a,b)=re.subn("\s","",x)
    return a

def load_input(filename):
    # load file with predicates and remove transform it into a form, where
    # single item in the output list contains1 represents a single predicate
    fn = open(filename, "r")
    contains=fn.readlines()
    contains = [remove_eol(con) for con in contains]
    contains1=[]
    for line in contains:
        if line=="":
            # skip empty lines
            continue
        elif re.search("^#",line):
            # skip comments
            continue
        elif re.search("RootCall",line):
            contains1.append(line)
        elif re.search("Params",line):
            contains1.append(line)
        elif re.search("Root",line):
            contains1.append(line)
        elif re.search(".*::=",line):
            contains1.append(line)
        else:
            if len(contains1)>0:
                contains1[len(contains1)-1]=contains1[len(contains1)-1]+line
    contains1 = [remove_whitespaces(con) for con in contains1]
    return contains1


def parse_predicate(pred,parsed_preds):
    # parse the input file into the intermediate format using regular expression
    # the return values are 0: single points-to in each rule, 1: empty-rule
    
    if not (re.search("^[^:=]*::=[^:]*$",pred)):
        raise InputError("The predicate %s has not a correct form."%pred)
    pred_name=re.sub("\(.*\)::=.*$","",pred)
    if pred_name in parsed_preds:
        raise InputError("multiple definition of predicate %s"%pred_name)
    pred_par=re.sub('^.*\((.*)\)::=.*$','\\1',pred)
    pred_par=re.split(",",pred_par)
    pred=re.sub("^.*::=","",pred)
    pred=re.split("\|",pred)
    rules=[]
    emp_rules=0
    for rule in pred:
        #------------------------------------------    
        # if the rule is empty (no allocation), parse it separatelly
        if not (re.search("->",rule)):
            # remove "[&]emp" from the rule"
            if re.search("\\*",rule):
                raise InputError("Parsing %s: now * allowed in empty rules"%rule)
            rule1=re.sub("[\\&]*emp","",rule)
            # add "&" at the beginning for simpler parsing
            rule1=re.sub("^([^\\&])","&\\1",rule1)
            eq_rel=[] # an equality relation between variables
            while(re.search("\\&",rule1)):
                # pick a single equality
                eq=re.sub("^\\&([^\\*\\&]*).*$","\\1",rule1)
                eq=re.split("=",eq)
                rule1=re.sub("^\\&[^\\*\\&]*","",rule1)
                if not len(eq)==2:
                    raise InputError("Parsing %s: only equalities of the form x=y separated by & are allowed"%rule)
                added=0

                for x in eq_rel:
                    if (eq[0] in x) and eq[1] in x:
                        added=1
                        break
                    if eq[0] in x:
                        x.append(eq[1])
                        added=1
                        break
                    if eq[1] in x:
                        x.append(eq[0])
                        added=1
                        break
                if not added:
                    eq_rel.append(eq)
            # remove variables, which are not parameters from eq_rel
            new_eq_rel=[]
            for cl in eq_rel:
                new_cl=[]
                for var in cl:
                    if (var in pred_par)or(var=="nil"):
                        new_cl.append(var)
                if len(new_cl)>1:
                    new_eq_rel.append(new_cl)
            # eq_rel now contains an equality relation between parameters

            rules.append(Rule("",[],[],new_eq_rel, []))
            emp_rules=1
            continue
            # end of empty rule parsing
        #------------------------------------------    
        # non-empty rule (with points-to predicate)
        if (re.search("^\\\\E",rule)):
            exists=re.sub('^\\\\E([^\.]*)\..*$','\\1',rule)
            exists=re.split(",",exists)
        else:
            exists=[]
        rule=re.sub("\\\\E[^\.]*\.","",rule)
        alloc=re.sub("([^-]*)->.*$","\\1",rule)
        pointsto=re.sub("[^-]*->([^\\*\\&]*).*$","\\1",rule)
        pointsto=re.split(",",pointsto)
        if re.search("->.*\\*.*->",rule):
            raise InputError("two pointsto in a single predicate rules -- not implemented")
        rule=re.sub("[^-]*->[^\\*\\&]*","",rule)
        equal=[]
        not_equal = []
        # parse pure part of the rule (i.e. equalities)
        while(re.search("\\&",rule)):
            eq=re.sub("^\\&([^\\*\\&]*).*$","\\1",rule)
            # only disequalities of the form alloc!=nil are allowed. Added just for the SMT-COMP
            if "!=" in eq:
                eq=re.split("!=",eq)
                if (eq[0]==alloc and eq[1]=="nil") or (eq[1]==alloc and eq[0]=="nil"):
                    pass
                else:
                    not_equal.append((eq[0], eq[1]))

                    #raise InputError("only disequalities of the for alloc!=nil are allowed")
            else:
                eq=re.split("=",eq)
                if not (len(eq)==2):
                    raise InputError("Only equalities between two variables are allowed in pure part")
                if eq[0]==alloc:
                    equal.append(eq[1])
                elif eq[1]==alloc:
                    equal.append(eq[0])
                else:
                    raise InputError(" only equalities between allocated variable and something are allowed")
            rule=re.sub("^\\&[^\\*\\&]*","",rule)        
        # replace equalities in points-to directly by the allocated node
        for x in range(0,len(pointsto)):
            if pointsto[x] in equal:
                pointsto[x]=alloc

        calles=[]
        while (re.search("\\*",rule)):
            call=re.sub("^\*([^\(]*)\(.*$","\\1",rule)
            call_params=re.sub("^\*[^\(]*\(([^\)]*)\).*$","\\1",rule)
            call_params=re.split(",",call_params)
            # replace equalities in the calls directly by the allocated node
            for x in range(0,len(call_params)):
                if call_params[x] in equal:
                    call_params[x]=alloc
            calles.append((call,call_params))
            rule=re.sub("^\*[^\*]*","",rule)
        rules.append(Rule(alloc,pointsto ,calles, equal, not_equal))
    
    parsed_preds[pred_name]=(Predicate(pred_name, pred_par, rules))
    return emp_rules
    
def alloc(pr,param_no,preds):
    # check whether the (param_no)^th parameter of the predicate "pr" is 
    # allocated in all its rules
    (params,rules)= preds[pr]
    res=1
    for (al,pt,calls,equal) in rules:
        if not (params[param_no] in [al]+equal):
            res=0
    return res

def points_to(pr,param_no,preds):
    # check whether the (param_no)^th parameter of the predicate "pr" is 
    # refered in all its rules
    (params,rules)= preds[pr]
    res=1
    for (al,pt,calls,equal) in rules:
        if (not params[param_no] in pt) or (params[param_no] in [al]+equal):
            res=0
    return res

def fw_edge(pr,param_no,preds):
    # check, whether the (param_no)^th parameter of the predicate "pr" is referenced
    # from all rules, where "pr" is called 
    #--- the forward local edge is created
    res=1
    for p in preds.keys():
        (params,rules)= preds[p]
        for (al,pt,calls,equal) in rules:
            for (call_name,call_pars) in calls:
                if call_name==pr:
                    if not (call_pars[param_no] in pt):
                        res=0
    return res
            
def bw_edge(pr,param_no,preds):
    # check, whether the (param_no)^th parameter of the predicate "pr" is allocated
    # in all rules, where "pr" is called 
    #--- the backward local edge is created
    res=1
    for p in preds.keys():
        (params,rules)= preds[p]
        for (al,pt,calls,equal) in rules:
            for (call_name,call_pars) in calls:
                if call_name==pr:
                    if not (call_pars[param_no] in [al]+equal ):
                        res=0
    return res
    

def compute_signature(preds):
    # for each predicate, compute signatures ---
    # i.e. each formal parameter is assigned to one of the following categories
    # sig_fw: forward local edge is passed via this parameter
    # sig_bw: backward local edge is passed via this parameter
    # sig_eq: "extra edge" is passed via this parameter (NOT YET IMPLEMENTED)    
    sig={}
    for p in preds.keys():
        (params,rules)= preds[p]
        sig_fw=[]
        sig_bw=[]
        sig_eq=[]
        for k in range(0,len(params)):
            if params[k]=='':
                continue
            if alloc(p,k,preds) and fw_edge(p,k,preds):
                sig_fw.append(k)
            if points_to(p,k,preds) and bw_edge(p,k,preds):
                sig_bw.append(k)
            if not(k in sig_fw or k in sig_bw):
                #raise InputError("Extra edges are not allowed")
                sig_eq.append(k)
        sig[p]=(sig_fw,sig_bw,sig_eq)
    return sig
        

def sl2ta(preds,sig,global_params,tiles,root_rule):
    # create the finite tree automaton and a set of tiles based on
    # the preprocessed system of predicates and its signatures
    #'fin': 'f',
    aut={'rules': [],'fin': root_rule}
    eq_edges=0
    for p in preds.keys():
        (sig_fw,sig_bw,sig_eq)=sig[p]
        (params,rules)= preds[p]
        # check that root rule has no parameters
        if p==root_rule and not (params==[''] or params==[]):
            raise InputError("Root predicate has parameters")
        for (al,pt,calls,equal) in rules:
            x_sets=[]
            lhs=[]
            null=[]
            self=[]
            par=[]            
            if al in global_params:
                par.append("al:%s"%al)
            for x in equal:
                if x in global_params:
                    par.append("al:%s"%x)
            # sort the parameters (it will be done in equal way for all the rules)
            par=sorted(par)
            for x in range(0,len(pt)):
                if (pt[x] in global_params) and not (pt[x] in [al]+equal):
                    par.append("%i:%s"%(x,pt[x]))
                if pt[x]==al:
                    self.append(x)
                if pt[x]=="nil":
                    null.append(x)
                tmp=1
            x_m1=[]
            for x in sig_bw:
                x_m1.append(pt.index(params[x]))
            x_m1=sorted(x_m1)
            for x in sig_eq:
                if params[x] in equal+[al]:
                    x_m1.append("al")
                elif params[x] in pt:
                    x_m1.append("s%i"%pt.index(params[x]))
                else:
                    x_m1.append("X"+params[x])
                eq_edges=1
            # create the sets x_i^{fw} for i>=0 and place them into x_sets array
            for (call_name,call_pars) in calls:
                xi=[]
                (c_fw,c_bw,c_eq)=sig[call_name]
                for s in c_fw:
                    xi.append(pt.index(call_pars[s]))
                xi=sorted(xi) # sort variable indicies
                for s in c_eq:
                    if call_pars[s] in equal+[al]:
                        xi.append("al")
                    elif call_pars[s] in pt:
                        xi.append("s%i"%pt.index(call_pars[s]))
                    else:
                        xi.append("X"+call_pars[s])
                    eq_edges=1
                x_sets.append(xi)
                lhs.append(call_name)
            # x_m1 contains input ports
            # x_sets now contains output ports
            #sort output ports according to selectors in paralel with lhs (the automata states)
            (x_sets,lhs)=functions.paralel_sort(x_sets,lhs)
            x_sets=[x_m1] + x_sets 
            tile=(x_sets,null,self,par)
            tile=functions.tile_normalize(tile)
            symbol=functions.tile_index(tile,tiles) # get an index to tiles list and use it as alphabet symbol
            aut['rules'].append((symbol,lhs,p))
    return aut,eq_edges

#---------------------------------------------------
# inline empty rules + create a formula for empty heap
#---------------------------------------------------

# We first define auxiliary functions for working with lists of equalities
# A conjunction of equalities is represented as list ot lists as e.q:
# x=y /\ y=z /\ a=b will be represented as [['x','y','z'],['a','b']]

def remove_multiple_occurences(a):
# remove multiple occurences of variables in a list of equalities
# example: [x,y,z,x] ----> [x,y,z]
    res=[]
    while not a==[]:
        x=a.pop()
        res.append(x)
        while x in a:
            a.pop(a.index(x))
    return res

def intersect_lists(a,b):
# check intersection between the lists a and b
# return the number of elements in the intersection
    number=0
    for x in a:
        if x in b:
            number=number+1
    return number

def join_equalities(a):
# join equlities
# example: [[x,y],[y,z],[a,b]] ---> [[x,y,z],[a,b]]
    res=[]
    joined=0
    for x in a:
        added=0
        for y in res:
            if  intersect_lists(x,y):
                y.extend(list(x))
                added=1
                joined=1 # something was joined
        if not added:
            res.append(list(x))
    if joined:
        # do a transitive closure till nothing is joined
        res=join_equalities(res)
    return res

def get_param_numbers(a,b):
# returns a list of positions of the item b in the list a 
    return [item for item in range(len(a)) if a[item] == b]

def match_params(inline_par,inline_eq,call_params):
# match parameters between a predicate call (call_params) and an empty rule (inline_params)
# then compute equalities inherited by the call
    equal1=[]
    for eq_list in inline_eq:
        eq1_list=[]
        for var in eq_list:
            if var=="nil":
                eq1_list.append("nil")
            else:
                for x in get_param_numbers(inline_par,var):
                    eq1_list.append(call_params[x])
        equal1.append(eq1_list)
    equal1=join_equalities(equal1)
    equal2=[]
    for x in equal1: 
        y=remove_multiple_occurences(x)
        if len(y)>1:
            equal2.append(y)
    return equal2
            
def create_new_rule(al,pt,calls,equal,pred_params,new_equalities,new_calls):
    # first check, whether the allocated node is in the equality relations
    eq_to_al=-1
    new_eq=list(equal)
    for i in range(len(new_equalities)):
        if (al in new_equalities[i]) or (intersect_lists(equal,new_equalities[i])):
            if eq_to_al>=0:
                raise InputError("This line should be unaccesible")
            if "nil" in new_equalities[i]:
                raise InputError("ERROR: inlining empty rules cause nil equal to an allocated node")
            eq_to_al=i
            new_eq.extend( new_equalities[i])
            new_eq=remove_multiple_occurences(new_eq)
    # pop the part of equalities equal to the allocated node
    if eq_to_al>=0:
        new_equalities.pop(eq_to_al)
    # go through the rest of equalities and place 
    new_pt=list(pt)
    for x in new_equalities:
        tmp=intersect_lists(x,pred_params)
        if tmp>=2:
            raise InputError("Create_new_rule: Not implemented")
        # get a representative
        if tmp==1:
            if "nil" in x:
                raise InputError("ERROR: formal parameter of nonempty rule equal to nil, Not implemented")
            for p in pred_params:
                if p in x:
                    repres=p
        else:
            if "nil" in x:
                repres="nil"
            else:
                repres=x[0]
        # replace all occurences by a representative
        for i in range(len(new_pt)):
            if new_pt[i] in x:
                new_pt[i]=repres
        for (pname,cparams) in new_calls:
            for i in range(len(cparams)):
                if cparams[i] in x:
                    cparams[i]=repres
    return (al,new_pt,new_calls,new_eq)

def inline_single_rule(preds):
    # pick an empty predicate rule and inline it
    find=0
    for x in preds.keys():
        (par,rules)= preds[x]
        empty=0
        nonempty=0
        for i in range(len(rules)):
            (al,pt,calls,equal)=rules[i]
            if al=="":
                if not( calls==[] and pt==[]): 
                    raise InputError("Something odd hapaned: the predicate %s contains an empty with nonempty calls"%x)
                inline_pred=x
                inline_par=par
                inline_eq=equal
                find=1
                if len(rules)==1:
                    # pop the whole predicate
                    preds.pop(x)
                    single=1
                else:
                    # pop the current rule
                    rules.pop(i)
                    single=0
                break
        if find:
            # stop the loop if rule is find
            break
    if not find:
        # no empty rules
        return 0
    #print "inlining :",inline_pred,inline_par,inline_eq
    # inline the rule
    for x in preds.keys():
        (par,rules)= preds[x]
        rule_to_remove=[]
        new_rules=[]
        for i in range(len(rules)):
            (al,pt,calls,equal)=rules[i]    
            new_eq_calls=[([],[],0)]
            for (pname,params) in calls:
                if pname==inline_pred:
                    #new_equalities.append(match_params(inline_par,inline_eq,params))
                    new_equalities=match_params(inline_par,inline_eq,params)
                    if single:
                        # we are inlining a single rule only
                        (eq,cls,flag)=new_eq_calls[0]
                        eq.extend(new_equalities)
                        join_equalities(eq)
                        new_eq_calls[0]=(eq,cls,flag+1)
                    else:
                        # we are inlining a rule from a predicate, which contains more rules
                        toadd=[]
                        for (eq,cls,flag) in new_eq_calls:
                            #CASE 1: inline
                            eq1=list(eq)
                            cls1=list(cls)
                            eq1.extend(list(new_equalities))
                            eq1=join_equalities(eq1)
                            toadd.append((eq1,cls1,flag+1))
                            # CASE 2: do not inline
                            cls.append((pname,params))
                        new_eq_calls.extend(toadd)
                else:
                    for (eq,new_cls,flag) in new_eq_calls:
                        new_cls.append((pname,params))
            # create a new rule according to the computed equalities
            aux=1
            for (eq,new_cls,flag) in new_eq_calls:
                if flag:
                    if single and aux:
                        # mark the current rule to be removed
                        rule_to_remove.append(i)
                        aux=0
                    # create a new rule for each item in new_eq_calls
                    new_rules.append(create_new_rule(al,pt,calls,equal,par,eq,new_cls))

        # remove the rules marked as "to be removed"
        nrules=[]
        for i in range(len(rules)):
            if not (i in rule_to_remove):
                nrules.append(rules[i])

        # exten the set of old rules by the newly created ones
        nrules.extend(new_rules)
        preds[x]=(par,nrules)

    return 1





def inline_empty_rules(preds,root_calls):
    eq_on_empty=[]
    for (root_pred,params) in root_calls:
        # check whether the root_predicate contains empty rules
        emptyheap_eq=[]
        (par,rules)=preds[root_pred]
        for (al,pt,calls,equal) in rules:
            if al=="":
                emptyheap_eq.append(equal)
    
        #substitute formal parameters of the empty rule by global parameters
        for i in range(len(emptyheap_eq)):
            new_disjunct=[]
            for disjunct in emptyheap_eq[i]:
                new_eq=[]
                for var in disjunct:            
                    if var=="nil":
                        new_eq.append("nil")
                    else:
                        pos=get_param_numbers(par,var)
                        if not len(pos)==1:
                            raise InputError("Problem with mapping parameters to empty heap")
                        new_eq.append(params[pos[0]])
                new_disjunct.append(new_eq)
            new_disjunct_join=join_equalities(new_disjunct)
            new_disjunct_join2=[]
            for q in new_disjunct_join:
                new_disjunct_join2.append(remove_multiple_occurences(q))
            emptyheap_eq[i]=new_disjunct_join2
        eq_on_empty.append(emptyheap_eq)
    
    # inline the empty rules
    while inline_single_rule(preds):
        pass
    return eq_on_empty


                    
                    
#--------------------------------------------------
# track end elimintate parameters
# >>> trackeliminate must be run before sl2ta
#--------------------------------------------------
# auxiliary functions for trackeliminate
def unique_pred_prefix(preds,pref):
    for x in preds.keys():
        if re.search("^%s"%pref,x):
            return 0
    return 1

def propagated(var_name,calls):
# get a direction, in which the parameter is propagated
# -1 no propagation
# -2 multiple propagation
    num=0
    tp_return=("no_propagation",-1,-1)
    for i in range(0,len(calls)):
        p_name,params=calls[i]
        occur=params.count(var_name)
        if occur==1 and num==0:
            num=1
            tp_return=(p_name,i,params.index(var_name))
        elif occur>=1: #multiple occurence
            return ("multiple_propagation",-2,-2)
    return tp_return

def propagated_new(var_name,calls):
# this function replace the original function "propagated"
# get a list containing directions, in which the parameter is propagated
# [] no propagation
# -2 double propagation: call(var_name,var_name)
    tp_return=[]
    for i in range(0,len(calls)):
        p_name,params=calls[i]
        occur=params.count(var_name)
        if occur==1:
            tp_return.append((p_name,i,params.index(var_name)))
        elif occur>1: #double occurence
            return (-1)
    return tp_return

def delete_call_item(prop_item,v_num,calls):
    (p_name,params)=calls[prop_item]
    mod_params=list(params) # make a fresh copy
    mod_params.pop(v_num)
    calls[prop_item]=(p_name,mod_params)
    return calls

def change_call_item_pred(prop_item,prefix,v_num,dlt,calls):
    p_name,params=calls[prop_item]
    calls[prop_item]=("%sx%sx%ix%i"%(prefix,p_name,v_num,dlt),params)
    return calls


def trackeliminate(preds,root,v_num,tracked,ex_quantif):
    # tracked - the name of the tracked parameter
    # ex_quantif (true/false) - the tracked variable is existantially quantified on the top level
    prefix="X%i"%v_num
    while unique_pred_prefix(preds,prefix)==0:
        prefix=prefix+"X"
    TODO=[(root,v_num,1)]    
    DONE=[]
    new_root="%sx%sx%ix1"%(prefix,root,v_num)
    while len(TODO):
        (p_name,v_num,dlt)=TODO.pop()
        DONE.append((p_name,v_num,dlt))
        # get a copy of parameters 
        new_params=list(preds[p_name][0])
        if dlt: 
            # remove the parameter v_num
            var_name=new_params.pop(v_num)
        else:
            var_name=new_params[v_num]
        # for all rules of the given predicate
        new_rules=[]
        for (alloc,pointsto,calls,equal) in preds[p_name][1]:
            if var_name==alloc or var_name in equal:
                if tracked=="nil":
                    #allocated node equal to nil -> ERROR
                    raise InputError("ERROR: allocated node equal to nil")
                new_eq=list(equal)
                if not ex_quantif: # if the tracked variable is free variable, then add it as equal to allocated node
                    new_eq.append(tracked)
                new_rules.append((alloc,pointsto,calls,new_eq))
            elif var_name in pointsto:
                #(prop_pred,prop_item,prop_num)=propagated(var_name,calls)
                prop_calls=propagated_new(var_name,calls)
                if prop_calls==-1:
                    raise InputError("ERROR: tracked parameter propagated as two independent variables, not implemented")
                if tracked=="nil":
                    # the case when tracked is equal to nil is handled separatelly
                    if not dlt:
                        raise InputError("ERROR: something odd hapaned. Tracking parameter equal to nil and dlt==0")
                    new_pointsto=[]
                    for i in pointsto:
                        if var_name==i:
                            new_pointsto.append(tracked)
                        else:
                            new_pointsto.append(i)
                    new_calls=list(calls)
                    for (prop_pred,prop_item,prop_var_num) in prop_calls:
                        new_calls=delete_call_item(prop_item,prop_var_num,list(new_calls))
                        new_calls=change_call_item_pred(prop_item,prefix,prop_var_num,dlt,new_calls)
                        if not(((prop_pred,prop_var_num,dlt) in DONE) or ((prop_pred,prop_var_num,dlt) in TODO)):
                            TODO.append((prop_pred,prop_var_num,dlt))
                    new_rules.append((alloc,new_pointsto,new_calls,equal))

                elif len(prop_calls)==0 and ex_quantif:
                    raise InputError("ERROR: dangling pointer reference, not covered")
                elif len(prop_calls)==0:
                    if new_params.count(var_name):
                        # we do not cover the following situations:
                        #  pred(a1,...,a1)::= x->( ,a1, ), where a1 is the tracked variable
                        #  pred(a1,...)::= x->( ,a1, ), dlt==0 and a1 is no more propagated
                        raise InputError("ERROR: parameter %s occures in the rule %s  more then once or no allocation"%(var_name, p_name))
                    new_pointsto=[]
                    for i in pointsto:
                        if var_name==i:
                            new_pointsto.append(tracked)
                        else:
                            new_pointsto.append(i)
                    new_rules.append((alloc,new_pointsto,calls,equal))                
                elif ex_quantif: 
                    # parameter is existentially quantified 
                    # => just add the original rule and do nothing else
                    new_rules.append((alloc,pointsto,calls,equal))
                elif len(prop_calls)==1:
                    (prop_pred,prop_item,prop_num)=prop_calls[0]
                    new_calls=change_call_item_pred(prop_item,prefix,prop_num,0,list(calls))
                    new_rules.append((alloc,pointsto,new_calls,equal))
                    if not(((prop_pred,prop_num,0) in DONE) or ((prop_pred,prop_num,0) in TODO)):
                        TODO.append((prop_pred,prop_num,0))
                else:
                    raise InputError("ERROR: variable %s not propagated from the rule %s"%(tracked,p_name))
            else:
                #(prop_pred,prop_item,prop_var_num)=propagated(var_name,calls)
                prop_calls=propagated_new(var_name,calls)
                if prop_calls==-1:
                    raise InputError("ERROR: tracked parameter propagated as two independent variables, not implemented")
                if len(prop_calls)==1:
                    (prop_pred,prop_item,prop_var_num)=prop_calls[0]
                    if dlt:
                        new_calls=delete_call_item(prop_item,prop_var_num,list(calls))
                    else:
                        new_calls=list(calls)
                    # change the predicate name in the item "prop_item"
                    new_calls=change_call_item_pred(prop_item,prefix,prop_var_num,dlt,new_calls)
                    new_rules.append((alloc,pointsto,new_calls,equal))
                    if not(((prop_pred,prop_var_num,dlt) in DONE) or ((prop_pred,prop_var_num,dlt) in TODO)):
                        TODO.append((prop_pred,prop_var_num,dlt))
                else:
                    
                    # tracked variable is no more propagated or it is propagated in two directions
                    # existential quantified tracked -> OK, add original rule
                    # nil tracked -> continue in all directions (dlt must be set to 1, othervice it does not make sense)
                    # free tracked -> STOP and raise an error
                    if tracked=="nil" and dlt:
                        new_calls=list(calls)
                        for (prop_pred,prop_item,prop_var_num) in prop_calls:
                            new_calls=delete_call_item(prop_item,prop_var_num,list(new_calls))
                            new_calls=change_call_item_pred(prop_item,prefix,prop_var_num,dlt,new_calls)
                            if not(((prop_pred,prop_var_num,dlt) in DONE) or ((prop_pred,prop_var_num,dlt) in TODO)):
                                TODO.append((prop_pred,prop_var_num,dlt))
                        new_rules.append((alloc,pointsto,new_calls,equal))
                    elif ex_quantif:
                        new_rules.append((alloc,pointsto,calls,equal))
                    else:
                        raise InputError("ERROR: variable %s not propagated (or multiple propagated) from the rule %s"%(tracked,p_name))

        # add the newly created predicate into a list of predicates
        preds["%sx%sx%ix%i"%(prefix,p_name,v_num,dlt)]=(new_params,new_rules)
    return new_root
                    
def remove_unreachable_predicates(preds,root):
    # first compute reachable predicates starting from the root
    reachable=[root]
    TODO=[root]
    while not TODO==[]:
        actual=TODO.pop()
        (par,rules)= preds[actual]
        for (al,pt,calls,equal) in rules:
            for (call_name,call_pars) in calls:
                if not call_name in reachable:
                    reachable.append(call_name)
                    TODO.append(call_name)
    # pop unreachable items
    for i in preds.keys():
        if not i in reachable:
            preds.pop(i)

#--------------------------------------------------
# conflicts between parameters and predicates 
# >>> rename_conflicts_with_params must be run before trackeliminate
#--------------------------------------------------

def unique_var_prefix(prefix,preds,params):
    # check, whether "prefix" is a part of a name of any variable in predicates "preds" and parameters "params"
    # 0 = NO: there is  no variable containing prefix
    # 1 = YES: there is a variable containing prefix
    for p in preds.keys():
        (par,rules)= preds[p]
        for x in par:
            if prefix in x:
                return 1
        for (al,pt,calls,equal) in rules:
            if prefix in al:
                return 1
            for x in pt:
                if prefix in x:
                    return 1
            for x in equal:
                if prefix in x:
                    return 1
            for (call_name,call_pars) in calls:
                for x in call_pars:
                    if prefix in x:
                        return 1
    for p in params:
        if prefix in p:
            return 1
    return 0


def rename_conflicts_with_params(preds,pars):
    # rename all variables equal to some parameter from "params" by adding an unique prefix
    # First, we remove all "nil" parameters
    params=[]
    for i in pars:
        if i!="nil":
            params.append(i)
    # create an unique prefix
    prefix="X"
    while unique_var_prefix(prefix,preds,params):
        prefix=prefix+"X"
    # no we will go through the systme of predicates and rename each variable "v" from params to "prefix+v"
    for p in preds.keys():
        (par,rules)= preds[p]
        new_par=[]
        for x in par:
            if x in params:
                new_par.append(prefix+x)
            else:
                new_par.append(x)
        new_rules=[]
        for (al,pt,calls,equal) in rules:
            if al in params:
                al1=prefix+al
            else:
                al1=al
            pt1=[]
            for x in pt:
                if x in params:
                    pt1.append(prefix+x)
                else:
                    pt1.append(x)

            equal1=[]
            for x in equal:
                if x in params:
                    equal1.append(prefix+x)
                else:
                    equal1.append(x)
            calls1=[]
            for (call_name,call_pars) in calls:
                call_pars1=[]
                for x in call_pars:
                    if x in params:
                        call_pars1.append(prefix+x)
                    else:
                        call_pars1.append(x)
                calls1.append((call_name,call_pars1))
            new_rules.append((al1,pt1,calls1,equal1))
        preds[p]=((new_par,new_rules))

# ----------------------------------------

def get_unique_name(pref,contains):
    # get an unique predicate name before the predicates are parsed
    candidate=pref
    stop=1
    while stop:
        stop=0
        for line in contains:
            if re.search("^%s"%candidate,line):
                stop=1
                candidate=candidate+"X"
                break
    return candidate



#-------------------------------------
# SL2TA
# step 1: load input
# step 2: parse predicates
# step 3: rename_conflicts_with_params (skipped in old version for compatibility reasons)
# step 4: track & eliminate parameters (skipped in old version for compatibility reasons)
# step 5: remove unreachable predicates (skipped in old version for compatibility reasons)
# step 6: sl2ta
#------------------------------------

def add_implicit_exists(ex_vars,globalfreevars,varlist):
    for v in varlist:
        if (globalfreevars=="ALL") or (v in globalfreevars) or (v in ex_vars) or (v=="nil"):
            pass
        else:
            ex_vars.append(v)
    

def parse_input(filename, globalfreevars):
    #tiles is a global list of actually known tiles
    # it is used to synchronise symbols between multiple automata
    # globalfreevars con
    contains=load_input(filename)
    preds={}
    params = ""
    root_rule = ""
    if (re.search("^RootCall",contains[0])):
        # NEW version
        # parse the "RootCall"
        # first check, whether there are existentially quentified parameters
        ex_params=[]
        if (re.search("^RootCall\\\\E",contains[0])):
            ex_params=re.sub('^RootCall\\\\E([^\.]*)\..*$','\\1',contains[0])
            ex_params=re.split(",",ex_params)
            contains[0]=re.sub("\\\\E([^\.]*)\.","",contains[0])

        # first check, whether the join operation is needed --- RootCall contains "*"
        rootcall=re.sub('^RootCall',"",contains[0])
        del contains[0]
        top_calls = CallsContainer()
        pt_seq=0

        while (re.search("\\*",rootcall)):
            # first handle "->" predicate
            if re.search("^[^\*]*->",rootcall):
                lhs=re.sub("^([^-]*)->.*$","\\1",rootcall)
                rhs=re.sub("^[^-]*->([^\*]*)\*.*$","\\1",rootcall)
                rhs=re.split(",",rhs)
                # remove nil and double occurences from rhs
                rhs_not_nil=[]
                for x in rhs:
                    if (not x=="nil") and (not x==lhs) and (not x in rhs_not_nil):
                        rhs_not_nil.append(x)
                # create an unique predicate for the points-to
                pred_name=get_unique_name("pt%i"%pt_seq,contains)
                pt_seq=pt_seq+1
                top_calls.append(TopCall(pred_name, [lhs]+rhs_not_nil))
                rule=(lhs,rhs,[],[])
                preds[pred_name]=(Predicate(pred_name, [lhs]+rhs_not_nil,
                                            [Rule(rule[0], rule[1], rule[2], rule[3], [])]))
                # do implicit quantification
                add_implicit_exists(ex_params,globalfreevars,[lhs]+rhs_not_nil)
            else:
                # store the predicate call into top_calls
                call=re.sub("^([^\(]*)\(.*$","\\1",rootcall)
                call_params=re.sub("^[^\(]*\(([^\)]*)\).*$","\\1",rootcall)
                call_params=re.split(",",call_params)
                top_calls.append(TopCall(call, call_params))
                # do implicit quantification
                add_implicit_exists(ex_params,globalfreevars,call_params)
            # remove the call
            rootcall=re.sub("^[^\*]*\*","",rootcall)
        if re.search("^[^\*]*->",rootcall):
            lhs=re.sub("^([^-]*)->.*$","\\1",rootcall)
            rhs=re.sub("^[^-]*->([^\*]*)$","\\1",rootcall)

            not_equal = []
            if '&' in rhs:
                rhs, rest = rhs.split('&', 1)
                rest = '&' + rest

                while(re.search("\\&",rest)):
                    eq=re.sub("^\\&([^\\*\\&]*).*$","\\1",rest)
                    # only disequalities of the form alloc!=nil are allowed. Added just for the SMT-COMP
                    if "!=" in eq:
                        eq=re.split("!=",eq)
                        if (eq[0]==alloc and eq[1]=="nil") or (eq[1]==alloc and eq[0]=="nil"):
                            pass
                        else:
                            not_equal.append((eq[0], eq[1]))

                            #raise InputError("only disequalities of the for alloc!=nil are allowed")
                    else:
                        eq=re.split("=",eq)
                        if not (len(eq)==2):
                            raise InputError("Only equalities between two variables are allowed in pure part")
                        if eq[0]==alloc:
                            equal.append(eq[1])
                        elif eq[1]==alloc:
                            equal.append(eq[0])
                        else:
                            raise InputError(" only equalities between allocated variable and something are allowed")
                    rest=re.sub("^\\&[^\\*\\&]*","", rest)

            rhs=re.split(",",rhs)
            # remove nil and double occurences from rhs
            rhs_not_nil=[]
            for x in rhs:
                #if not x=="nil":
                if (not x=="nil") and (not x==lhs) and (not x in rhs_not_nil):
                    rhs_not_nil.append(x)
            # create an unique predicate for the points-to
            pred_name=get_unique_name("pt%i"%pt_seq,contains)
            pt_seq=pt_seq+1
            top_calls.append(TopCall(pred_name,[lhs]+rhs_not_nil))
            rule=(lhs,rhs,[],[])
            preds[pred_name]=(Predicate(pred_name, [lhs]+rhs_not_nil,
                                            [Rule(rule[0], rule[1], rule[2], rule[3], not_equal)]))
            # do implicit quantification
            add_implicit_exists(ex_params,globalfreevars,[lhs]+rhs_not_nil)
        else:
            call=re.sub("^([^\(]*)\(.*$","\\1",rootcall)
            call_params=re.sub("^[^\(]*\(([^\)]*)\).*$","\\1",rootcall)
            call_params=re.split(",",call_params)
            top_calls.append(TopCall(call,call_params))
            # do implicit quantification
            add_implicit_exists(ex_params,globalfreevars,call_params)
        type=2
    else:
        # OLD version just for compatibility reasons
        # get parameters
        if not (re.search("^Params",contains[0])):
            raise InputError("No \"Params\" specified on 1st (nonempty) line of input")
        params=re.sub("^Params","",contains[0])
        params=re.split(",",params)
        del contains[0]
        # get root rule identifier
        if not (re.search("^Root",contains[0])):
            raise InputError("No \"Root\" specified on 2st (nonempty) line of input")
        root_rule=re.sub("^Root","",contains[0])
        del contains[0]
        type=0
    #Parse predicates
    empty_rule=0

    for x in contains:
        empty_rule=empty_rule+parse_predicate(x,preds)
    return preds, top_calls, params, root_rule, empty_rule


def make_aut(preds, top_calls, params, root_rule, empty_rule, tiles):
    if empty_rule:
        # empty rules in the system of predicates -> inline them + create a formula for empty heap
        emptyheap_eq=inline_empty_rules(preds,top_calls)
    else:
        emptyheap_eq=[] # No empty heap defined by the system of predicates ---> false represented as []
    if type==2:
        # type==2: join operator on top level calls to translate into a single Rootcall
        (root_rule,params,emptyheap_eq)=join.join(preds,top_calls,emptyheap_eq,ex_params)

        # rename all variables in conflict between parameters and predicates
        rename_conflicts_with_params(preds,params)
        #track and eliminate all parameters
        for i in range(0,len(params)):
            ex_quantif=(params[i] in ex_params) # or (params[i]=="nil") # nil is allways handled as existentially quantified variable
            root_rule=trackeliminate(preds,root_rule,0,params[i],ex_quantif)
        # remove unreachable predicates
        remove_unreachable_predicates(preds,root_rule)
        # remove "nil" from params
        new_params=[]
        for i in params:
            if i!="nil" and not (i in ex_params):
                new_params.append(i)
        params=new_params
        # remove ex_params from emptyheap_eq
        new_emptyheap_eq=[]
        for disj in emptyheap_eq:
            new_disj=[]
            for conj in disj:
                new_conj=[]
                for x in conj:
                    if not x in ex_params:
                        new_conj.append(x)
                if len(new_conj)>1:
                    new_disj.append(new_conj)
            new_emptyheap_eq.append(new_disj)
        emptyheap_eq=new_emptyheap_eq

    else:
        # OLD version, just for compatibility reasons (type==0)
        if not emptyheap_eq==[]:
            emptyheap_eq=emptyheap_eq[0]

    sig=compute_signature(preds)
    aut,eq_edges=sl2ta(preds,sig,params,tiles,root_rule)
    #if eq_edges:
    #    print "WARNING: equality edges in use"
    return aut,emptyheap_eq,eq_edges
        
#--------------------------------------------------------------------------------
# for the integration into the SMT-COMP, we need an implicit existential quantification 
# of all variables in the RootCall, which are free only on LHS, or only on RHS.
# Therefore we need to colect all free variables from the input file

def get_free_variables(filename):
    contains=load_input(filename)
    if (re.search("^RootCall",contains[0])):
        # parse the "RootCall"
        # first check, whether there are existentially quentified parameters
        ex_params=[]
        if (re.search("^RootCall\\\\E",contains[0])):
            ex_params=re.sub('^RootCall\\\\E([^\.]*)\..*$','\\1',contains[0])
            ex_params=re.split(",",ex_params)
            contains[0]=re.sub("\\\\E([^\.]*)\.","",contains[0])

        # first check, whether the join operation is needed --- RootCall contains "*"
        rootcall=re.sub('^RootCall',"",contains[0])
        free_vars=[]

        while (re.search("\\*",rootcall)):
            # first handle "->" predicate
            if re.search("^[^\*]*->",rootcall):
                lhs=re.sub("^([^-]*)->.*$","\\1",rootcall)
                rhs=re.sub("^[^-]*->([^\*]*)\*.*$","\\1",rootcall)
                rhs=re.split(",",rhs)
                free_vars.extend([lhs]+rhs)
            else:
                # store the predicate call into top_calls
                call_params=re.sub("^[^\(]*\(([^\)]*)\).*$","\\1",rootcall)
                call_params=re.split(",",call_params)
                free_vars.extend(call_params)
            # remove the call
            rootcall=re.sub("^[^\*]*\*","",rootcall)
        if re.search("^[^\*]*->",rootcall):
            lhs=re.sub("^([^-]*)->.*$","\\1",rootcall)
            rhs=re.sub("^[^-]*->([^\*]*)$","\\1",rootcall)
            rhs=re.split(",",rhs)
            free_vars.extend([lhs]+rhs)
        else:
            call_params=re.sub("^[^\(]*\(([^\)]*)\).*$","\\1",rootcall)
            call_params=re.split(",",call_params)
            free_vars.extend(call_params)
        # remove "nil" and variables from ex_params
        free_vars=remove_multiple_occurences(free_vars)
        result=[]
        for x in free_vars:
            if (not x=="nil")and (not x in ex_params):
                result.append(x)
        return result
    else:
        # all variables are considered to be free in the old version
        return "ALL"

