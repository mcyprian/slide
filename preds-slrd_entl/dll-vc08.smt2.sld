Entail LHS(x_emp,y_emp,z_emp,w_emp,u_emp,t_emp) |- RHS(x_emp,y_emp,z_emp,w_emp,u_emp,t_emp)


LHS(x_emp,y_emp,z_emp,w_emp,u_emp,t_emp) ::= w_emp->t_emp,u_emp & x_emp!=w_emp & w_emp!=t_emp & z_emp!=w_emp * dll(x_emp,u_emp,nil,w_emp) * dll(t_emp,y_emp,w_emp,z_emp)

RHS(x_emp,y_emp,z_emp,w_emp,u_emp,t_emp) ::= dll(x_emp,y_emp,nil,z_emp)

dll(fr,bk,pr,nx) ::=  fr=nx & bk=pr & emp |
  \E u . fr->u,pr & fr!=nx & bk!=pr * dll(u,bk,fr,nx)
