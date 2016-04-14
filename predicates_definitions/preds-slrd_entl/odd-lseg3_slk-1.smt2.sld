Entail LHS(a,x,p) |- RHS(a,x,p)


LHS(a,x,p) ::= x->a * a->p

RHS(a,x,p) ::= olseg(x,p)

olseg(in,p) ::=  in->p |
  \E a,b . in->a * a->b * olseg(b,p)
