Entail LHS(x,y) |- RHS(x,y)


LHS(x,y) ::= ListX(x,y)

RHS(x,y) ::= List(x,y)

ListE(x,y) ::=  \E xp . x->xp & nil!=x * ListO(xp,y)

ListO(x,y) ::=  x->y & nil!=x |
  \E xp . x->xp & nil!=x * ListE(xp,y)

ListX(x,y) ::=  ListO(x,y) |
  ListE(x,y)

List(x,y) ::=  x->y & nil!=x |
  \E xp . x->xp & nil!=x * List(xp,y)
