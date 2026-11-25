    .text
# @alku hae
# int32_t hae(const int32_t *t, long i): osoite lasketaan erikseen.
    .globl hae
hae:
    slli a1, a1, 2              # i * 4
    add a0, a0, a1              # t + i * 4
    lw a0, 0(a0)
    ret
# @loppu hae

# @alku arvo
# int64_t varaston_arvo(const struct tuote *t, long n)
    .globl varaston_arvo
varaston_arvo:
    li t0, 0                    # summa = 0
    blez a1, 2f                 # n <= 0: tyhjä varasto
1:  lw t1, 4(a0)                # t->maara (etumerkillinen 32 bittiä)
    ld t2, 8(a0)                # t->hinta_snt
    mul t1, t1, t2
    add t0, t0, t1
    addi a0, a0, 16             # seuraava tuote
    addi a1, a1, -1
    bnez a1, 1b
2:  mv a0, t0
    ret
# @loppu arvo
    .section .note.GNU-stack,"",@progbits
