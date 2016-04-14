Entail LHS(a,b,z,p) |- RHS(a,b,z,p)


LHS(a,b,z,p) ::= z->a * a->b * elseg(b,p)

RHS(a,b,z,p) ::= right(z,p)

elseg(in,p) ::=  in=p & emp |
  \E a,b . in->a * a->b * elseg(b,p)

right(in,p) ::=  \E u . elseg(in,u) * elseg(u,p)
