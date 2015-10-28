Entail LHS(x,y,z,w) |- RHS(x,y,z,w)


LHS(x,y,z,w) ::= DLL(x,y,z,w)

RHS(x,y,z,w) ::= SLL(x,y)

SLL(x,y) ::=  x=y & emp |
  \E xp,yp . x->xp,yp & nil!=x * SLL(xp,y)

DLL(x,y,z,w) ::=  x=y & z=w & emp |
  \E zp . x->zp,w & nil!=x * DLL(zp,y,z,x)
