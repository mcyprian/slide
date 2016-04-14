Entail LHS(x,q,z,p) |- RHS(x,q,z,p)


LHS(x,q,z,p) ::= z->x * q->p * elseg(x,q)

RHS(x,q,z,p) ::= right(z,p)

elseg(in,p) ::=  in=p & emp |
  \E a,b . in->a * a->b * elseg(b,p)

right(in,p) ::=  \E u . elseg(in,u) * elseg(u,p)
