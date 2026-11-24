    .text
    .globl    tilauksen_arvo
tilauksen_arvo:
    pxor    %xmm0, %xmm0
    cvtsi2sdl    4(%rdi), %xmm0
    mulsd    8(%rdi), %xmm0
    ret
    .globl    tilauksen_asiakas
tilauksen_asiakas:
    movq    16(%rdi), %rax
    ret
