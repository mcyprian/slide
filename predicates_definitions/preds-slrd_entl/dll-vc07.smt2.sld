Entail LHS(x_emp,w_emp,y_emp,z_emp) |- RHS(x_emp,w_emp,y_emp,z_emp)


LHS(x_emp,w_emp,y_emp,z_emp) ::= x_emp->w_emp,nil & x_emp!=w_emp & x_emp!=z_emp * dll(w_emp,y_emp,x_emp,z_emp)

RHS(x_emp,w_emp,y_emp,z_emp) ::= dll(x_emp,y_emp,nil,z_emp)

dll(fr,bk,pr,nx) ::=  fr=nx & bk=pr & emp |
  \E u . fr->u,pr & fr!=nx & bk!=pr * dll(u,bk,fr,nx)
