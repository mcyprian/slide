Entail LHS(x,y,z,x1,x2,x3,x4) |- RHS(x,y,z,x1,x2,x3,x4)


LHS(x,y,z,x1,x2,x3,x4) ::= x->x1,nil * x1->x2,x * x2->x3,x1 * x3->x4,x2 * x4->y,x3 * y->z,x4 & x!=z & z!=x1 & z!=x2 & z!=x3 & z!=x4 & y!=z

RHS(x,y,z,x1,x2,x3,x4) ::= dll(x,y,nil,z)

dll(fr,bk,pr,nx) ::=  fr=nx & bk=pr & emp |
  \E u . fr->u,pr & fr!=nx & bk!=pr * dll(u,bk,fr,nx)
