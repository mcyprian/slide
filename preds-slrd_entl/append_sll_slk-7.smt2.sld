Entail LHS(q,xprm,yprm,y,x) |- RHS(q,xprm,yprm,y,x)


LHS(q,xprm,yprm,y,x) ::= xprm->q & nil!=q & xprm=x & yprm=y & nil!=x * ll(q)

RHS(q,xprm,yprm,y,x) ::= nil!=q & xprm=x & yprm=y & nil!=x * ll(x)

ll(in) ::=  nil=in & emp |
  \E q_18 . in->q_18 * ll(q_18)

ll_e1(in) ::=  \E q . in->q * ll(q)

ll_e2(in) ::=  \E p,q . in->p & p=q * ll(q)

node_e1(in,q) ::=  \E p . in->p & q=p
