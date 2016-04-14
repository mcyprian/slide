Entail LHS(x,p) |- RHS(x,p)


LHS(x,p) ::= x->p

RHS(x,p) ::= olseg(x,p)

olseg(in,p) ::=  in->p |
  \E a,b . in->a * a->b * olseg(b,p)
