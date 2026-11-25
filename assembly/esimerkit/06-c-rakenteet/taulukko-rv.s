    .text
    .globl    taulukon_summa
taulukon_summa:
    ble    a1,zero,.L4
    slli    a1,a1,3
    mv    a5,a0
    add    a3,a0,a1
    li    a0,0
.L3:
    ld    a4,0(a5)
    addi    a5,a5,8
    add    a0,a0,a4
    bne    a5,a3,.L3
    ret
.L4:
    li    a0,0
    ret
