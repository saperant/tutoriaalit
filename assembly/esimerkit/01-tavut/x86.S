# Kaksi pientä funktiota, joiden konekielinen koodaus luetaan
# objdumpilla.
    .text
    .globl kaksinkertaista
kaksinkertaista:                # long kaksinkertaista(long x)
    lea (%rdi,%rdi), %rax       # rax = x + x
    ret

    .globl summaa
summaa:                         # long summaa(long a, long b)
    mov %rdi, %rax
    add %rsi, %rax
    ret
    .section .note.GNU-stack,"",@progbits
