    .text
    .globl    kertoma
kertoma:
    mv    a5,a0
    li    a0,1
    li    a3,1
    ble    a5,a0,.L1
.L2:
    mv    a4,a5
    addi    a5,a5,-1
    mul    a0,a0,a4
    bne    a5,a3,.L2
.L1:
    ret
