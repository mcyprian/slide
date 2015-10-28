Entail LHS(x,y,z) |- RHS(x,y,z)


LHS(x,y,z) ::= y->z * ls(x,y) * ls(z,nil)

RHS(x,y,z) ::= ls(x,z) * ls(z,nil)

ls(x,y) ::=  x=y & emp |
  \E xp . x->xp & nil!=x & x!=y * ls(xp,y)
