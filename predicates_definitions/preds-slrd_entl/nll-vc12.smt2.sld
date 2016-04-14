Entail LHS(x1,x1_1,x2,x2_1) |- RHS(x1,x1_1,x2,x2_1)


LHS(x1,x1_1,x2,x2_1) ::= x1->x2,x1_1 * x2->nil,x2_1 * lso(x1_1,nil) * lso(x2_1,nil)

RHS(x1,x1_1,x2,x2_1) ::= nll(x1,nil,nil)

lso(in,out) ::=  in=out & emp |
  \E u . in->u & in!=out * lso(u,out)

nll(in,out,boundary) ::=  in=out & emp |
  \E u,Z1 . in->u,Z1 & in!=out * lso(Z1,boundary) * nll(u,out,boundary)
