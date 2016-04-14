Entail LHS(a,b,x,p) |- RHS(a,b,x,p)


LHS(a,b,x,p) ::= x->a * a->b * elseg(b,p)

RHS(a,b,x,p) ::= elseg(x,p)

elseg(in,p) ::=  in=p & emp |
  \E a,b . in->a * a->b * elseg(b,p)

right(in,p) ::=  \E u . elseg(in,u) * elseg(u,p)
