Entail LHS(x,y,z,w) |- RHS(x,y,z,w)


LHS(x,y,z,w) ::= DLL(x,y,z,w)

RHS(x,y,z,w) ::= BSLL(z,w)

BSLL(x,y) ::=  x=y & emp |
  \E xp,yp . xp->yp,y & nil!=xp * BSLL(x,xp)

DLL(x,y,z,w) ::=  x=y & z=w & emp |
  \E zp . x->zp,w & nil!=x * DLL(zp,y,z,x)
