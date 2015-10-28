Entail LHS(p,x) |- RHS(p,x)


LHS(p,x) ::= lseg(x,p)

RHS(p,x) ::= right4(x)

lseg(in,p) ::=  in=p & emp |
  \E a . in->a * lseg(a,p)

right1(in,p) ::=  \E u . u->p * lseg(in,u)

right2(in,p) ::=  \E u . lseg(in,u) * lseg(u,p)

right3(in,p) ::=  \E u,u2 . lseg(in,u) * lseg(u,u2) * lseg(u2,p)

right4(in) ::=  \E u,w . lseg(in,u) * lseg(u,w)

right5(in) ::=  \E w . lseg(in,w)
