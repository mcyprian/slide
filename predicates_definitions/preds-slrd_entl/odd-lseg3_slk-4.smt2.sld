Entail LHS(b,x,p) |- RHS(b,x,p)


LHS(b,x,p) ::= x->b * olseg(b,p)

RHS(b,x,p) ::= olseg(x,p)

olseg(in,p) ::=  in->p |
  \E a,b . in->a * a->b * olseg(b,p)
