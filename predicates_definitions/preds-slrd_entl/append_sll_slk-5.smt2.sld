Entail LHS(v1prm,xprm,yprm,y,x,q) |- RHS(v1prm,xprm,yprm,y,x,q)


LHS(v1prm,xprm,yprm,y,x,q) ::= xprm->q & v1prm=q & nil!=q & xprm=x & yprm=y & nil!=x * ll(q) * ll(y)

RHS(v1prm,xprm,yprm,y,x,q) ::= xprm->q & v1prm=q & nil!=q & xprm=x & yprm=y & nil!=x & nil!=v1prm * ll(v1prm) * ll(yprm)

ll(in) ::=  nil=in & emp |
  \E q_18 . in->q_18 * ll(q_18)

ll_e1(in) ::=  \E q . in->q * ll(q)

ll_e2(in) ::=  \E p,q . in->p & p=q * ll(q)

node_e1(in,q) ::=  \E p . in->p & q=p
