Entail LHS(x,y) |- RHS(x,y)


LHS(x,y) ::= ls(x,y) * ls(y,nil)

RHS(x,y) ::= ls(x,nil)

ls(x,y) ::=  x=y & emp |
  \E xp . x->xp & nil!=x & x!=y * ls(xp,y)
