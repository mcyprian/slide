Entail LHS(x,y,z) |- RHS(x,y,z)


LHS(x,y,z) ::= x->y * RList(y,z)

RHS(x,y,z) ::= RList(x,z)

RList(x,y) ::=  x->y & nil!=x |
  \E xp . xp->y & nil!=xp * RList(x,xp)
