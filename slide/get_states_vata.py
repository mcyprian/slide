#!/usr/bin/python3
#
# Adam Rogalewicz
# 
# SL to TA - top level calls
# distrubuted under GNU GPL licence


import sys
import re

def remove_eol(x):
    return re.sub("\n","",x)

def remove_whitespaces(x):
    (a,b)=re.subn("\s","",x)
    return a



def get_states(filename):
    fn = open(filename, "r")
    contains=fn.readlines()
    fn.close()
    contains= [remove_eol(con) for con in contains]
    while not (re.search("Transitions",contains[0])):
        del contains[0]
    print("----")
    del contains[0]
    states=[]
    for line in contains:
        x=remove_whitespaces(line)
        y=re.sub("^[^\(]*\(([^\)]*)\)->(.*)$","\\1,\\2",x)
        z=re.split(",",y)
        for a in z:
            if a=='':
                continue
            if not (a in states):
                states.append(a)
    print("Stavu: ",len(states))



get_states(sys.argv[1])
