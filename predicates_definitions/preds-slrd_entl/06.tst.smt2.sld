Entail LHS(x,y,z) |- RHS(x,y,z)


LHS(x,y,z) ::= PeList(x,y) * PeList(y,z)

RHS(x,y,z) ::= PeList(x,z)

PeList(x,y) ::=  x=y & emp |
  \E xp . x->xp & nil!=x * PeList(xp,y)
