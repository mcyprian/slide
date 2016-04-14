Entail LHS(x,y,z) |- RHS(x,y,z)


LHS(x,y,z) ::= BinPath(x,z) * BinPath(z,y)

RHS(x,y,z) ::= BinPath(x,y)

BinPath(x,y) ::=  x=y & emp |
  \E xp,yp . x->xp,yp & nil!=x * BinPath(xp,y) |
  \E xp,yp . x->xp,yp & nil!=x * BinPath(yp,y)
