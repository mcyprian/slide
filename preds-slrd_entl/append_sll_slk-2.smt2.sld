Entail LHS(xprm,vprm,yprm,y,x,q) |- RHS(xprm,vprm,yprm,y,x,q)


LHS(xprm,vprm,yprm,y,x,q) ::= xprm->q & nil=vprm & vprm=q & xprm=x & yprm=y & nil!=x * ll(q) * ll(y)

RHS(xprm,vprm,yprm,y,x,q) ::= xprm->q & nil=vprm & vprm=q & xprm=x & yprm=y & nil!=x * ll(q) * ll(y)

ll(in) ::=  nil=in & emp |
  \E q_18 . in->q_18 * ll(q_18)

ll_e1(in) ::=  \E q . in->q * ll(q)

ll_e2(in) ::=  \E p,q . in->p & p=q * ll(q)

node_e1(in,q) ::=  \E p . in->p & q=p
