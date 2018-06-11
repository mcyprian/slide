SLIDE - Separation Logic with Inductive Definitions
=======

Automata-based entailment checking for Separation Logic with Inductive Definitions
---------------

SLIDE is a prototype tool for checking entailment in Separation Logic with
user-provided inductive definitions of recursive data structures (lists, trees,
and beyond) 

![SLIDE home page](http://www.fit.vutbr.cz/research/groups/verifit/tools/slide/)

Basic features:
---------------

    - Sound and complete for local data structures (doubly-linked lists, trees with parent pointers, etc.)
    - Sound for non-local data structures (trees with linked leaves, skip-lists, etc. )
    - Built on top of the VATA tree automata library.

Requirements:
---------------
![VATA](https://github.com/ondrik/libvata) tree automata library.

Python 3

Usage:
---------------
    mybin.py [-h] [--run xhs xhs] [--performance-check PERFORMANCE_CHECK]
                    [--result-comparision RESULT_COMPARISION RESULT_COMPARISION]
    
    optional arguments:
      -h, --help            show this help message and exit
      --run xhs xhs         input files containing definitions of lhs rhs.
      --performance-check PERFORMANCE_CHECK
                            Run check of current slide performance.
      --result-comparision RESULT_COMPARISION RESULT_COMPARISION
                            Compare results of two previous checks.
