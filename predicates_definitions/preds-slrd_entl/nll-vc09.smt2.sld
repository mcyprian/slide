Entail LHS(x1,x2,x2_1,x2_2,x3) |- RHS(x1,x2,x2_1,x2_2,x3)


LHS(x1,x2,x2_1,x2_2,x3) ::= x2->x3,x2_1 * x2_1->x2_2 * nll(x1,x2,nil) * lso(x2_2,nil) * nll(x3,nil,nil)

RHS(x1,x2,x2_1,x2_2,x3) ::= nll(x1,nil,nil)

lso(in,out) ::=  in=out & emp |
  \E u . in->u & in!=out * lso(u,out)

nll(in,out,boundary) ::=  in=out & emp |
  \E u,Z1 . in->u,Z1 & in!=out * lso(Z1,boundary) * nll(u,out,boundary)
