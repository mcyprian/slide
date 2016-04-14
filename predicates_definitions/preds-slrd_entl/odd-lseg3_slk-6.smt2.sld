Entail LHS(p,a,k,b) |- RHS(p,a,k,b)


LHS(p,a,k,b) ::= k->b * p->a * a->b * olseg(b,p)

RHS(p,a,k,b) ::= olseg(k,b)

olseg(in,p) ::=  in->p |
  \E a,b . in->a * a->b * olseg(b,p)
