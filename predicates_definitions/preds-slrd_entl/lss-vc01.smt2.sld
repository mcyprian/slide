Entail LHS(x_emp,y_emp,z_emp) |- RHS(x_emp,y_emp,z_emp)


LHS(x_emp,y_emp,z_emp) ::= x_emp->y_emp,y_emp * y_emp->z_emp,z_emp

RHS(x_emp,y_emp,z_emp) ::= lsso(x_emp,z_emp)

lsso(in,out) ::=  in=out & emp |
  \E u . in->u,u * lsso(u,out)
