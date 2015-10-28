Entail LHS(x,y,z) |- RHS(x,y,z)


LHS(x,y,z) ::= x->y & x!=z * ls(y,z)

RHS(x,y,z) ::= ls(x,z)

ls(x,y) ::=  x=y & emp |
  \E xp . x->xp & nil!=x & x!=y * ls(xp,y)
