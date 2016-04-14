Entail LHS(x1,x1_1,x1_2,x1_3,x2,x3,x3_1,x3_2) |- RHS(x1,x1_1,x1_2,x1_3,x2,x3,x3_1,x3_2)


LHS(x1,x1_1,x1_2,x1_3,x2,x3,x3_1,x3_2) ::= x1->x2,x1_1 * x1_1->x1_2 * x1_2->x1_3 * x1_3->nil * x3->nil,x3_1 * x3_1->x3_2 * x3_2->nil * nll(x2,x3,nil)

RHS(x1,x1_1,x1_2,x1_3,x2,x3,x3_1,x3_2) ::= nll(x1,nil,nil)

lso(in,out) ::=  in=out & emp |
  \E u . in->u & in!=out * lso(u,out)

nll(in,out,boundary) ::=  in=out & emp |
  \E u,Z1 . in->u,Z1 & in!=out * lso(Z1,boundary) * nll(u,out,boundary)
