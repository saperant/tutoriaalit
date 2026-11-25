    .text
    .globl    valita
valita:
    leaq    1(%rdi,%rdi), %rdi
    jmp    tarkista@PLT
