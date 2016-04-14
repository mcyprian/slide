Entail LHS(x,y,z) |- RHS(x,y,z)


LHS(x,y,z) ::= BinTreeSeg(x,y) * BinTree(y)

RHS(x,y,z) ::= BinTree(x)

BinTree(x) ::=    emp |
  \E yp,xp . x->yp,xp & nil!=x * BinTree(yp) * BinTree(xp)

BinTreeSeg(x,y) ::=  x=y & emp |
  \E xp,yp . x->xp,yp & nil!=x * BinTreeSeg(xp,y) * BinTree(yp) |
  \E xp,yp . x->xp,yp & nil!=x * BinTree(xp) * BinTreeSeg(yp,y)
