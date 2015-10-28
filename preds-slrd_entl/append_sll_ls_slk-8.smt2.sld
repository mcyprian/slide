Entail LHS(next0,q,xprm,yprm,x,y) |- RHS(next0,q,xprm,yprm,x,y)


LHS(next0,q,xprm,yprm,x,y) ::= xprm->yprm & next0=q & nil=q & xprm=x & yprm=y & nil!=x * ll(q)

RHS(next0,q,xprm,yprm,x,y) ::= next0=q & nil=q & xprm=x & yprm=y & nil!=x * lseg_e1(x,y) * ll(q)

ll(in) ::=  nil=in & emp |
  \E q_20 . in->q_20 * ll(q_20)

lseg(in,p) ::=  in=p & emp |
  \E p_19,q_18 . in->q_18 & p=p_19 * lseg(q_18,p_19)

ll_e1(in) ::=  \E q . in->q * ll(q)

ll_e2(in) ::=  \E p,q . in->p & p=q * ll(q)

node_e1(in,q) ::=  \E p . in->p & q=p

lseg_e1(in,p) ::=  \E q . p=q * lseg(in,p)
