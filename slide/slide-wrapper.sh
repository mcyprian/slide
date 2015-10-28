#!/bin/sh
# this script split the file created by  smt2sl into two separate files for lhs and rhs

writeerror() {
    echo "Error: $1" >&2
    exit 1
}

# replace all occurences of nil in calls in RHS/LHS by a fresh variable and add move nil to the Rootcall
handle_nil_in_root() {
    if grep "$2.*::=.*\*.*[(,]nil[),]" $1 >/dev/null; then
        newvar="newn"
        # create a fresh variable
        while grep "$newvar" $1; do
            newvar="X$newvar"
        done
        tmpfile=$(mktemp)
        while grep "$2.*::=.*\*.*[(,]nil[),]" $1 >/dev/null; do
            sed "s/\($2.*::=.*\*.*[(,]\)nil\([),].*\)$/\1$newvar\2/" < $1 \
            | sed "s/$2(\([^)]*\)) *::=/$2(\1,$newvar) ::=/" \
            | sed "s/RootCall *$2(\([^)]*\))/RootCall $2(\1,nil)/" >$tmpfile
            newvar="X$newvar"
            cp $tmpfile $1

            
        done
    fi

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
#if grep 'ls(in,out) ::=  in=out |' $1 > /dev/null &&  grep '\\E u . in->u \& in!=out \* ls(u,out)' $1 >/dev/null; then
#    inf=$(mktemp)
#    sed 's/\\E u . in->u \& in!=out \* ls(u,out)/\\E u . in->u \* ls(u,out)/' < $1 | sed 's/\& nil=nil //' > $inf 
#else
#    inf=$1
#fi
inf=$1
#--------------------------------------------

# create temporary files for LHS and RHS
lhs=$(mktemp)
rhs=$(mktemp)

if grep "^[[:space:]]*LHS.*::=.*->" $inf >/dev/null && ! grep  "^[[:space:]]*LHS.*::=.*->.*->" $inf >/dev/null; then
    grep "Entail.*|-" $inf | sed "s/Entail[ ]*\(LHS[^|]*\)|-.*$/RootCall \1/" >>$lhs
    grep -v "Entail" $inf | grep -v "^[[:space:]]*RHS[[:space:]]*(.*::=" >> $lhs
    # nil in the LHS definition must be muved to the RootCall
    handle_nil_in_root $lhs "LHS"
else
    if grep "^[[:space:]]*LHS[[:space:]]*(" $inf >/dev/null; then
        true
    else
        writeerror "No LHS specified"
    fi
    grep "^[[:space:]]*LHS[[:space:]]*(" $inf | sed "s/^[ ]*LHS.*::=/RootCall /" >>$lhs
    grep -v "Entail" $inf | grep -v "^[[:space:]]*RHS[[:space:]]*(.*::=" | grep -v "^[[:space:]]*LHS[[:space:]]*(.*::=" >> $lhs
fi

if grep "^[[:space:]]*RHS.*::=.*->" $inf >/dev/null && ! grep  "^[[:space:]]*RHS.*::=.*->.*->" $inf >/dev/null; then
    grep "Entail.*|-" $inf | sed "s/Entail.*|-[[:space:]]*\(RHS.*\)$/RootCall \1/" >>$rhs
    grep -v "Entail" $inf | grep -v "^[[:space:]]*LHS[[:space:]]*(.*::="  >> $rhs
    # nil in the RHS definition must be muved to the RootCall
    handle_nil_in_root $rhs "RHS"
else
    if grep "^[[:space:]]*RHS[[:space:]]*(" $inf >/dev/null; then
        true
    else
        writeerror "No RHS specified"
    fi
    grep "^[[:space:]]*RHS[[:space:]]*(" $inf | sed "s/^[ ]*RHS.*::=/RootCall /" >>$rhs
    grep -v "Entail" $inf | grep -v "^[[:space:]]*RHS[[:space:]]*(.*::=" | grep -v "^[[:space:]]*LHS[[:space:]]*(.*::=" >> $rhs
fi


#echo "------"
#cat $lhs 
#echo "------"
#cat $rhs

python $dir/entailment.py   $lhs $rhs
