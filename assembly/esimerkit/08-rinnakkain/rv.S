    .text
# @alku lajittele
# void lajittele(long *t, long n): lisäyslajittelu osoittimilla.
    .globl lajittele
lajittele:
    li t0, 1                    # i = 1
1:  bge t0, a1, 4f              # i >= n: valmis
    slli t1, t0, 3
    add t1, a0, t1              # p = &t[i]
    ld t2, 0(t1)                # x = t[i]
2:  beq t1, a0, 3f              # p == &t[0]
    ld t3, -8(t1)               # p[-1]
    ble t3, t2, 3f              # p[-1] <= x: paikka löytyi
    sd t3, 0(t1)                # *p = p[-1]
    addi t1, t1, -8
    j 2b
3:  sd t2, 0(t1)                # *p = x
    addi t0, t0, 1
    j 1b
4:  ret
# @loppu lajittele
    .globl lajittele_loppu
lajittele_loppu:
    .section .note.GNU-stack,"",@progbits
