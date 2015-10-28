Entail LHS(a,b,x,y,z,w) |- RHS(a,b,x,y,z,w)


LHS(a,b,x,y,z,w) ::= DLL(x,y,z,w) * DLL(a,x,w,b)

RHS(a,b,x,y,z,w) ::= DLL(a,y,z,b)

DLL(x,y,z,w) ::=  x=y & z=w & emp |
  \E zp . x->zp,w & nil!=x * DLL(zp,y,z,x)
