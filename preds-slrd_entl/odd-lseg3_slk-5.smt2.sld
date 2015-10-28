Entail LHS(p,a,b) |- RHS(p,a,b)


LHS(p,a,b) ::= p->a * a->b * olseg(b,p)

RHS(p,a,b) ::= olseg(b,b)

olseg(in,p) ::=  in->p |
  \E a,b . in->a * a->b * olseg(b,p)
