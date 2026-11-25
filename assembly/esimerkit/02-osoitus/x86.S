    .text
# @alku hae
# int32_t hae(const int32_t *t, long i): kanta + indeksi * 4.
    .globl hae
hae:
    movl (%rdi,%rsi,4), %eax
    ret
# @loppu hae

# @alku arvo
# int64_t varaston_arvo(const struct tuote *t, long n)
# struct tuote { int32_t koodi; int32_t maara; int64_t hinta_snt; }
#                siirtymä 0      siirtymä 4      siirtymä 8, koko 16
    .globl varaston_arvo
varaston_arvo:
    xor %eax, %eax              # summa = 0
    test %rsi, %rsi
    jle 2f                      # n <= 0: tyhjä varasto
1:  movslq 4(%rdi), %rcx        # t->maara, laajennus 64 bittiin
    imul 8(%rdi), %rcx          # * t->hinta_snt
    add %rcx, %rax
    add $16, %rdi               # seuraava tuote
    dec %rsi
    jnz 1b
2:  ret
# @loppu arvo
    .section .note.GNU-stack,"",@progbits
