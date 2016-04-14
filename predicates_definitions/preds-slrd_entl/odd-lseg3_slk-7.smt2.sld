Entail LHS(p,a,b,k,g) |- RHS(p,a,b,k,g)


LHS(p,a,b,k,g) ::= k->b * p->a * a->b * b->g * olseg(b,p)

RHS(p,a,b,k,g) ::= olseg(k,g)

olseg(in,p) ::=  in->p |
  \E a,b . in->a * a->b * olseg(b,p)
