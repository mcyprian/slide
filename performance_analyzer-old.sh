#!/bin/bash

SMT2SL='/home/mcyprian/Codes/devel/smtcomp14-sl/smtlib2sl/compile'
SLIDE_WRAPPER='/home/mcyprian/Codes/devel/slide/slide/slide-wrapper.sh'
SLD_DEST='/home/mcyprian/Codes/devel/slide/preds-slrd_entl/'
SMT_SOURCE_DIR='/home/mcyprian/Codes/devel/smtcomp14-sl/bench/slrd_entl/'
SLD_UNSUCCESS='/home/mcyprian/Codes/devel/slide/slrd_entl_unsuccess/'
ERROR_MSG_FILE='/home/mcyprian/Codes/devel/slide/slrd_entl_unsuccess/error_msg_1'
ERROR_FREQUENCY_FILE='/home/mcyprian/Codes/devel/slide/slrd_entl_unsuccess/error_num_1'
SLD_SUFFIX='.sld'


clean(){
    rm $SLD_UNSUCCESS/*
    rm $SLD_DEST/*
    exit 0
}

convert_to_slide(){
    for file in $(ls $SMT_SOURCE_DIR); do
        if [ "$file" == "README" ]; then
            break
        fi
        $SMT2SL -slide $SMT_SOURCE_DIR$file
        mv $SMT_SOURCE_DIR$file$SLD_SUFFIX $SLD_DEST
        STDERR=$(($SLIDE_WRAPPER "$SLD_DEST$file$SLD_SUFFIX") 2>&1)
        retval=$(($?))
        if [ $retval -ne 0 ]; then
            cp $SLD_DEST$file$SLD_SUFFIX $SLD_UNSUCCESS$file$SLD_SUFFIX
            echo "$file$SLD_SUFFIX:" >> "$ERROR_MSG_FILE"
            echo "$STDERR" >> "$ERROR_MSG_FILE"
            echo "" >> "$ERROR_MSG_FILE"
        fi
    done
}

check_performance(){
    ERROR_MSG_FILE="$ERROR_MSG_FILE"_1 
    ERROR_FREQUENCY_FILE="$ERROR_FREQUENCY_FILE"_1
    for file in $(ls $SLD_DEST); do
        STDERR=$(($SLIDE_WRAPPER "$SLD_DEST$file") 2>&1)
        retval=$(($?))
        if [ $retval -ne 0 ]; then
            echo "$file$SLD_SUFFIX:" >> "$ERROR_MSG_FILE"
            echo "$STDERR" >> "$ERROR_MSG_FILE"
            echo "" >> "$ERROR_MSG_FILE"
        fi
    done
}

get_errors_frequency(){
    echo "Countig frequency of errors:"
    errors=("impossible to join the input"
    "ERROR: dangling pointer reference"
    "JOIN: complicated join, not implemented"
    "only disequalities of the for alloc!=nil"
    "Parsing %s: only equalities of the form x=y separated"
    "only equalities between allocated variable"
    "NoneType' object has no attribute"
    "two pointsto in a single predicate rules"
    "Parsing \%s: now * allowed in empty rules")
    
    cd $SLD_UNSUCCESS
    
    touch $ERROR_MSG_FILE
    touch $ERROR_FREQUENCY_FILE
    
    for ((i = 0; i <  "${#errors[@]}"; i++)); do
        NUM=$((grep "${errors[$i]}" "$ERROR_MSG_FILE" | wc -l) 1>&1)
        echo "${errors[$i]}  $(($NUM/2))" >> "$ERROR_FREQUENCY_FILE"
        echo "${errors[$i]}  $NUM" 
    done
}

case $1 in 
    "clean")     clean;;
    "convert")   convert_to_slide; check_performance; get_errors_frequncy;; 
    "check")     check_performance; get_errors_frequency;;
esac

exit 0
