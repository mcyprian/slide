Entail LHS(next0,q,yprm,y,x,self,xprm,p,q1) |- RHS(next0,q,yprm,y,x,self,xprm,p,q1)


LHS(next0,q,yprm,y,x,self,xprm,p,q1) ::= xprm->p,yprm & nil=yprm & next0=q & nil=q & x=xprm & yprm=y & nil!=x & self=xprm & p=q1

RHS(next0,q,yprm,y,x,self,xprm,p,q1) ::= nil=yprm & next0=q & nil=q & x=xprm & yprm=y & nil!=x & self=xprm & p=q1 * dll_e3(x,q1)

dll(in,p) ::=  nil=in & emp |
  \E p_20,self_21,q_19 . in->p_20,q_19 & p=p_20 & in=self_21 * dll(q_19,self_21)

dll_e1(in,q) ::=  \E p1,s,q1 . in->p1,q1 & in=s & q=p1 * dll(q1,s)

dll_e2(in,q) ::=  \E s,p1,p2,n,q1 . in->p1,n & n=q1 & p1=p2 & in=s & q=p2 * dll(q1,s)

node2_e1(in,p,q) ::=  \E p1,n1 . in->p1,n1 & p=p1 & q=n1

dll_e3(in,p) ::=  \E q . p=q * dll(in,q)
