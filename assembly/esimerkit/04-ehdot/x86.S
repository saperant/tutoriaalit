    .text
# @alku pituus
# size_t pituus(const char *s): merkkijonon pituus (strlen).
    .globl pituus
pituus:
    mov %rdi, %rax              # p = s
1:  cmpb $0, (%rax)             # *p == 0?
    je 2f
    inc %rax                    # p++
    jmp 1b
2:  sub %rdi, %rax              # p - s
    ret
# @loppu pituus

# @alku rajaa
# long rajaa(long x, long ala, long yla): x rajattuna väliin.
    .globl rajaa
rajaa:
    mov %rdi, %rax
    cmp %rsi, %rax
    cmovl %rsi, %rax            # jos x < ala, x = ala
    cmp %rdx, %rax
    cmovg %rdx, %rax            # jos x > yla, x = yla
    ret
# @loppu rajaa
    .section .note.GNU-stack,"",@progbits
