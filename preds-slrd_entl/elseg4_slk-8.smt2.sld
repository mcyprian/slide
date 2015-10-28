Entail LHS(z,p) |- RHS(z,p)


LHS(z,p) ::= elseg(z,p)

RHS(z,p) ::= right(z,p)

elseg(in,p) ::=  in=p & emp |
  \E a,b . in->a * a->b * elseg(b,p)

right(in,p) ::=  \E u . elseg(in,u) * elseg(u,p)
