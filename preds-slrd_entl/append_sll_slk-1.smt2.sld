Entail LHS(xprm,yprm,y,x) |- RHS(xprm,yprm,y,x)


LHS(xprm,yprm,y,x) ::= xprm=x & yprm=y & nil!=x * ll_e1(xprm) * ll(y)

RHS(xprm,yprm,y,x) ::= xprm=x & yprm=y & nil!=x * ll_e2(xprm) * ll(y)

ll(in) ::=  nil=in & emp |
  \E q_18 . in->q_18 * ll(q_18)

ll_e1(in) ::=  \E q . in->q * ll(q)

ll_e2(in) ::=  \E p,q . in->p & p=q * ll(q)

node_e1(in,q) ::=  \E p . in->p & q=p
