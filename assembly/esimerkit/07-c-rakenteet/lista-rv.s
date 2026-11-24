    .text
    .globl    listan_summa
listan_summa:
    mv    a5,a0
    li    a0,0
    beq    a5,zero,.L4
.L3:
    ld    a4,0(a5)
    ld    a5,8(a5)
    add    a0,a0,a4
    bne    a5,zero,.L3
    ret
.L4:
    ret
