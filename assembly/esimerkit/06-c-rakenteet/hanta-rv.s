    .text
    .globl    valita
valita:
    slli    a0,a0,1
    addi    a0,a0,1
    tail    tarkista@plt
