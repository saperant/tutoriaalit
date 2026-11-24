    .text
    .globl    kertoma
kertoma:
    addi    sp,sp,-32
    sd    ra,24(sp)
    sd    s0,16(sp)
    addi    s0,sp,32
    sd    a0,-24(s0)
    ld    a4,-24(s0)
    li    a5,1
    bgt    a4,a5,.L2
    li    a5,1
    j    .L3
.L2:
    ld    a5,-24(s0)
    addi    a5,a5,-1
    mv    a0,a5
    call    kertoma
    mv    a4,a0
    ld    a5,-24(s0)
    mul    a5,a4,a5
.L3:
    mv    a0,a5
    ld    ra,24(sp)
    ld    s0,16(sp)
    addi    sp,sp,32
    jr    ra
