Entail LHS(a,x,p) |- RHS(a,x,p)


LHS(a,x,p) ::= x->a * elseg(a,p)

RHS(a,x,p) ::= elseg(x,p)

elseg(in,p) ::=  in=p & emp |
  \E a,b . in->a * a->b * elseg(b,p)

right(in,p) ::=  \E u . elseg(in,u) * elseg(u,p)
