    .text
    .globl    kymmenesosa
kymmenesosa:
    li    a5,10
    divu    a0,a0,a5
    ret
    .globl    kahdeksasosa
kahdeksasosa:
    srai    a5,a0,63
    andi    a5,a5,7
    add    a0,a5,a0
    srai    a0,a0,3
    ret
