# Miten globaalin datan osoitus ja vakiot koodataan (x86-64).
    .data
luku:
    .quad 7
    .text
osoitus:
    mov luku(%rip), %rax        # siirtymä rip:stä, linkkeri täyttää
    lea luku(%rip), %rdi
    mov $5, %eax                # 32-bittinen vakio, nollaa ylimmät
    mov $-1, %rax               # etumerkillä laajennettu 32 b vakio
    movabs $0x123456789abcdef0, %rax
    ret
    .section .note.GNU-stack,"",@progbits
