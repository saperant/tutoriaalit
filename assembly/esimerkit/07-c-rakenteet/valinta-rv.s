    .text
    .globl    laske
laske:
    li    a5,6
    bgtu    a0,a5,.L11
    lla    a4,.L4
    slli    a5,a0,2
    add    a5,a5,a4
    lw    a5,0(a5)
    add    a5,a5,a4
    jr    a5
    .section    .rodata
.L4:
    .word    .L10-.L4
    .word    .L9-.L4
    .word    .L8-.L4
    .word    .L7-.L4
    .word    .L6-.L4
    .word    .L5-.L4
    .word    .L3-.L4
    .text
.L5:
    xor    a0,a2,a1
    ret
.L3:
    sll    a0,a1,a2
    ret
.L10:
    add    a0,a2,a1
    ret
.L9:
    sub    a0,a1,a2
    ret
.L8:
    mul    a0,a2,a1
    ret
.L7:
    and    a0,a2,a1
    ret
.L6:
    or    a0,a2,a1
    ret
.L11:
    li    a0,0
    ret
