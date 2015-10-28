Entail LHS(x,y,z) |- RHS(x,y,z)


LHS(x,y,z) ::= ListE(x,y) * ListO(y,z)

RHS(x,y,z) ::= ListO(x,z)

ListE(x,y) ::=  \E xp . x->xp & nil!=x * ListO(xp,y)

ListO(x,y) ::=  x->y & nil!=x |
  \E xp . x->xp & nil!=x * ListE(xp,y)
