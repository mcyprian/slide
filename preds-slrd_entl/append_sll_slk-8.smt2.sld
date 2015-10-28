Entail LHS(next0,q,xprm,yprm,y,x) |- RHS(next0,q,xprm,yprm,y,x)


LHS(next0,q,xprm,yprm,y,x) ::= xprm->yprm & next0=q & nil=q & xprm=x & yprm=y & nil!=x * ll(q) * ll(y)

RHS(next0,q,xprm,yprm,y,x) ::= next0=q & nil=q & xprm=x & yprm=y & nil!=x * ll(x) * ll(q)

ll(in) ::=  nil=in & emp |
  \E q_18 . in->q_18 * ll(q_18)

ll_e1(in) ::=  \E q . in->q * ll(q)

ll_e2(in) ::=  \E p,q . in->p & p=q * ll(q)

node_e1(in,q) ::=  \E p . in->p & q=p
