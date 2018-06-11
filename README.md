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
