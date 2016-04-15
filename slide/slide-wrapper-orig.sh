#!/bin/sh
# this script split the file created by  smt2sl into two separate files for lhs and rhs

writeerror() {
    echo "Error: $1" >&2
    exit 1
}

# basic checks
if [ "X$1" == "X" ]; then
    echo "Usage: slide-wrapper.sh input_file"
    exit 
fi

if type dirname >/dev/null; then
    dir=$( dirname  $0 )
else
    dir="."
fi

if [ -f "$1" ]; then
    true
else
    writeerror "Input file $1 does not exists"
fi


#--------------------------------------------
# do some fixes for fixed ls examples created by smt2sl
if grep 'ls(in,out) ::=  in=out |' $1 > /dev/null &&  grep '\\E u . in->u \& in!=out \* ls(u,out)' $1 >/dev/null; then
    inf=$(mktemp)
    sed 's/\\E u . in->u \& in!=out \* ls(u,out)/\\E u . in->u \* ls(u,out)/' < $1 | sed 's/\& nil=nil //' > $inf 
else
    inf=$1
fi
#--------------------------------------------

# create temporary files for LHS and RHS
lhs=$(mktemp)
rhs=$(mktemp)

if grep "^[[:space:]]*LHS[[:space:]]*(" $inf >/dev/null; then
    true
else
    writeerror "No LHS specified"
fi
grep "^[[:space:]]*LHS[[:space:]]*(" $inf | sed "s/^[[:space:]]*LHS.*::=/RootCall /" >>$lhs
grep -v "Entail" $inf | grep -v "^[[:space:]]*RHS[[:space:]]*(.*::=" | grep -v "^[[:space:]]*LHS[[:space:]]*(.*::=" >> $lhs

if grep "^[[:space:]]*RHS[[:space:]]*(" $inf >/dev/null; then
    true
else
    writeerror "No RHS specified"
fi
grep "^[[:space:]]*RHS[[:space:]]*(" $inf | sed "s/^[[:space:]]*RHS.*::=/RootCall /" >>$rhs
grep -v "Entail" $inf | grep -v "^[[:space:]]*RHS[[:space:]]*(.*::=" | grep -v "^[[:space:]]*LHS[[:space:]]*(.*::=" >> $rhs


#echo "------"
#cat $lhs
#echo "------"
#cat $rhs

python3 $dir/entailment.py  $lhs $rhs
