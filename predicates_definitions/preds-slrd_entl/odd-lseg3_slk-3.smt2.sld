Entail LHS(a,b,x,p) |- RHS(a,b,x,p)


LHS(a,b,x,p) ::= x->a * a->b * olseg(b,p)

RHS(a,b,x,p) ::= olseg(x,p)

olseg(in,p) ::=  in->p |
  \E a,b . in->a * a->b * olseg(b,p)
