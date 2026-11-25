    .text
    .globl    ensimmainen
ensimmainen:
    addi    sp,sp,-48
    sd    s0,32(sp)
    la    s0,__stack_chk_guard
    mv    a0,sp
    ld    a5, 0(s0)
    sd    a5, 24(sp)
    li    a5, 0
    li    a1,24
    sd    ra,40(sp)
    call    tayta@plt
    ld    a4, 24(sp)
    ld    a5, 0(s0)
    xor    a5, a4, a5
    li    a4, 0
    lbu    a0,0(sp)
    bne    a5,zero,.L5
    ld    ra,40(sp)
    ld    s0,32(sp)
    addi    sp,sp,48
    jr    ra
.L5:
    call    __stack_chk_fail@plt
