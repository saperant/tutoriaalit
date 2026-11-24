# Sama RISC-V:llä: skalaari ja vektorilaajennus V, jonka vektorin
# pituutta ohjelma ei tiedä etukäteen (vsetvli kertoo sen).
    .option arch, +v
    .text
    .globl summa_skalaari
summa_skalaari:
    li t0, 0
1:  beqz a1, 2f
    lw t1, 0(a0)
    addw t0, t0, t1
    addi a0, a0, 4
    addi a1, a1, -1
    j 1b
2:  mv a0, t0
    ret

# @alku rvv
    .globl summa_rvv
summa_rvv:
    vsetvli t0, zero, e32, m1, ta, ma
    vmv.v.i v8, 0               # osasummat = 0
1:  beqz a1, 2f
    vsetvli t0, a1, e32, m1, tu, ma # t0 = käsiteltävien määrä
    vle32.v v9, (a0)            # lataa t0 alkiota
    vadd.vv v8, v8, v9          # tu: käsittelemättömät kaistat säilyvät
    sub a1, a1, t0
    slli t1, t0, 2
    add a0, a0, t1
    j 1b
2:  vsetvli t0, zero, e32, m1, ta, ma
    vmv.s.x v10, zero
    vredsum.vs v10, v8, v10     # kaistojen summa
    vmv.x.s a0, v10
    ret
# @loppu rvv
    .section .note.GNU-stack,"",@progbits
