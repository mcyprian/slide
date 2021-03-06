Entail LHS(xprm,vprm,yprm,y,x,q) |- RHS(xprm,vprm,yprm,y,x,q)


LHS(xprm,vprm,yprm,y,x,q) ::= xprm->q & nil=vprm & vprm=q & xprm=x & yprm=y & y=x & nil!=x * ll(q)

RHS(xprm,vprm,yprm,y,x,q) ::= xprm->q & nil=vprm & vprm=q & xprm=x & yprm=y & y=x & nil!=x * ll(q)

lseg(in,p) ::=  in=p & emp |
  \E p_21,q_20 . in->q_20 & p=p_21 * lseg(q_20,p_21)

ll(in) ::=  nil=in & emp |
  \E q_22 . in->q_22 * ll(q_22)

clist(in) ::=  \E self_19,p_18 . in->p_18 & in=self_19 * lseg(p_18,self_19)

ll_e1(in) ::=  \E q . in->q * ll(q)

ll_e2(in) ::=  \E p,q . in->p & p=q * ll(q)

node_e1(in,q) ::=  \E p . in->p & q=p

lseg_e1(in,p) ::=  \E q . p=q * lseg(in,p)
