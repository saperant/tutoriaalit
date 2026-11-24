    .text
# @alku kertoma
# long kertoma(long n): paluuosoite ja s0 tallennetaan pinokehykseen.
    .globl kertoma
kertoma:
    li t0, 1
    bgt a0, t0, 1f
    li a0, 1                    # n <= 1: 1
    ret
1:  addi sp, sp, -16            # kehys: 16 tavun monikerta
    sd ra, 8(sp)                # call korvaa ra:n
    sd s0, 0(sp)                # s0 on kutsutun tallennettava
    mv s0, a0                   # n talteen kutsun yli
    addi a0, a0, -1
    call kertoma                # a0 = (n - 1)!
    mul a0, a0, s0              # n * (n - 1)!
    ld s0, 0(sp)
    ld ra, 8(sp)
    addi sp, sp, 16
    ret
# @loppu kertoma

# @alku summa9
# long summa9(long a, ..., long i): kahdeksan argumenttia
# rekistereissä a0–a7, yhdeksäs pinossa.
    .globl summa9
summa9:
    add a0, a0, a1
    add a0, a0, a2
    add a0, a0, a3
    add a0, a0, a4
    add a0, a0, a5
    add a0, a0, a6
    add a0, a0, a7
    ld t0, 0(sp)                # i (9. argumentti)
    add a0, a0, t0
    ret
# @loppu summa9

# @alku kay_lapi
# long kay_lapi(const long *t, long n, long (*f)(long))
    .globl kay_lapi
kay_lapi:
    addi sp, sp, -48
    sd ra, 40(sp)
    sd s0, 32(sp)               # t
    sd s1, 24(sp)               # jäljellä olevien määrä
    sd s2, 16(sp)               # f
    sd s3, 8(sp)                # summa
    mv s0, a0
    mv s1, a1
    mv s2, a2
    li s3, 0
    blez s1, 2f
1:  ld a0, 0(s0)
    jalr s2                     # f(*t)
    add s3, s3, a0
    addi s0, s0, 8
    addi s1, s1, -1
    bnez s1, 1b
2:  mv a0, s3
    ld ra, 40(sp)
    ld s0, 32(sp)
    ld s1, 24(sp)
    ld s2, 16(sp)
    ld s3, 8(sp)
    addi sp, sp, 48
    ret
# @loppu kay_lapi
    .section .note.GNU-stack,"",@progbits
