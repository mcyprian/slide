Entail LHS(x,y,z) |- RHS(x,y,z)


LHS(x,y,z) ::= y->z * List(x,y)

RHS(x,y,z) ::= List(x,z)

List(x,y) ::=  x->y & nil!=x |
  \E xp . x->xp & nil!=x * List(xp,y)
