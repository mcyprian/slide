Entail LHS(x) |- RHS(x)


LHS(x) ::= BinListSecond(x)

RHS(x) ::= BinTree(x)

BinListSecond(x) ::=    emp |
  \E yp,xp . x->yp,xp & nil!=x * BinListSecond(xp)

BinTree(x) ::=    emp |
  \E yp,xp . x->yp,xp & nil!=x * BinTree(yp) * BinTree(xp)
