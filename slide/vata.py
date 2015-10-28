# Adam Rogalewicz
# 
# SL to TA prototype implementation
# distrubuted under GNU GPL licence

import os
import re
import functions
from settings import *
#tmp_dir="tmp"
#VATA_path="/home/rogalew/Experiments/libvata/build/cli/vata"

class VATAError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)



def aut_to_file(aut,filename,name):
    out=[]
    # VATA ignores "States" and "Ops", just the line must be present
    #ops=[]
#    states=[]
#    for (a,b,c) in aut['rules']:
#        if not (a in ops):
#            ops.append(a)
#        if not (c in states):
#            states.append(c)
#        for x in b:
#            if not x in states:
#                states.append(x)
#    opsfin="Ops "
#    states_str="States "
#    for x in ops:
#        opsfin=opsfin+"%s:0 "%x
#    for x in states:
#        states_str=states_str+"%s "%x
#    out.append(opsfin)
    out.append("Ops\n")
    out.append("\n\nAutomaton %s\n" % name)
#    out.append(states_str)
    out.append("States\n")
    out.append("\nFinal States %s\n" % aut['fin'])
    out.append("\nTransitions\n")
    for (a,b,c) in aut['rules']:
        rule="%i("% a
        comma=0
        for state in b:
            if comma:
                rule=rule+",%s"% state
            else:
                rule=rule+"%s"% state
                comma=1
        rule=rule+") -> %s\n" %c
        out.append(rule)
    file=open(filename,"w")
    file.writelines(out)
    file.close()
    

def call_vata_union(aut_list,filename):
    if aut_list==[]:
        raise VATAError("Empty list of automata")
    if len(aut_list)==1:
        aut_to_file(aut_list[0],filename,"result")    
        return
    #create a named temporary file
    tmp1=functions.get_tmp_filename()
    aut_to_file(aut_list[0],tmp1,"intermediate")
    for i in range(1,len(aut_list)):
        #create a named temporary file
        tmp2=functions.get_tmp_filename()
        aut_to_file(aut_list[i],tmp2,"intermediate")
        tmp3=functions.get_tmp_filename()
        os.system("%s union %s %s > %s"%(VATA_path,tmp1,tmp2,tmp3))
        #remove tmp files
        os.unlink(tmp1)
        os.unlink(tmp2)
        tmp1=tmp3
    # reduction is not implemented in some version of vata
    os.system("cp  %s %s"%(tmp1,filename))
    #os.system("%s red %s > %s"%(VATA_path,tmp1,filename))
    os.unlink(tmp1)

def remove_eol(x):
    return re.sub("\n","",x)

def remove_whitespaces(x):
    (a,b)=re.subn("\s","",x)
    return a

def get_states_vata(filename):
    fn = open(filename, "r")
    contains=fn.readlines()
    fn.close()
    contains=map(remove_eol,contains)
    while not (re.search("Transitions",contains[0])):
        del contains[0]
    del contains[0]
    states=[]
    for line in contains:
        x=remove_whitespaces(line)
        # rules of the form A -> q are substituted by X() -> q
        x=re.sub("^[^\(]->","X()->",x) 
        y=re.sub("^[^\(]*\(([^\)]*)\)->(.*)$","\\1,\\2",x)
        z=re.split(",",y)
        for a in z:
            if a=='':
                continue
            if not (a in states):
                states.append(a)
    return states

def get_trans_number(filename):
    fn = open(filename, "r")
    contains=fn.readlines()
    fn.close()
    contains=map(remove_eol,contains)
    rules=0
    for line in contains:
        if "->" in line:
            rules=rules+1
    return rules
    
