Entail LHS(q,q2,x,p) |- RHS(q,q2,x,p)


LHS(q,q2,x,p) ::= q->q2 * q2->p * elseg(x,q)

RHS(q,q2,x,p) ::= elseg(x,p)

elseg(in,p) ::=  in=p & emp |
  \E a,b . in->a * a->b * elseg(b,p)

right(in,p) ::=  \E u . elseg(in,u) * elseg(u,p)
