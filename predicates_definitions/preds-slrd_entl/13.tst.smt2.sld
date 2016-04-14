Entail LHS(x) |- RHS(x)


LHS(x) ::= BinListFirst(x)

RHS(x) ::= BinTree(x)

BinListFirst(x) ::=    emp |
  \E yp,xp . x->yp,xp & nil!=x * BinListFirst(yp)

BinTree(x) ::=    emp |
  \E yp,xp . x->yp,xp & nil!=x * BinTree(yp) * BinTree(xp)
