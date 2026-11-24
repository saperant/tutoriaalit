#include "../01-rajapinta/funktio.h"
    .text
# @alku vahti
# long vahdi(long (*f)(long), long x, unsigned *muuttuneet)
# Bitti n = rekisteri sn (s0–s11). Palauttaa f:n paluuarvon.
.macro tarkista rek, arvo, bitti
    li t1, \arvo
    beq \rek, t1, 9f
    li t1, 1 << \bitti
    or t2, t2, t1
9:
.endm

FUNKTIO(vahdi)
    addi sp, sp, -112
    sd ra, 104(sp)
    sd s0, 96(sp)
    sd s1, 88(sp)
    sd s2, 80(sp)
    sd s3, 72(sp)
    sd s4, 64(sp)
    sd s5, 56(sp)
    sd s6, 48(sp)
    sd s7, 40(sp)
    sd s8, 32(sp)
    sd s9, 24(sp)
    sd s10, 16(sp)
    sd s11, 8(sp)
    sd a2, 0(sp)                # muuttuneet
    .irp n, 0,1,2,3,4,5,6,7,8,9,10,11
    li s\n, 0x5a00 + \n
    .endr
    mv t0, a0
    mv a0, a1
    jalr t0                     # a0 = f(x)
    li t2, 0
    .irp n, 0,1,2,3,4,5,6,7,8,9,10,11
    tarkista s\n, 0x5a00 + \n, \n
    .endr
    ld t3, 0(sp)
    sw t2, 0(t3)
    ld s11, 8(sp)
    ld s10, 16(sp)
    ld s9, 24(sp)
    ld s8, 32(sp)
    ld s7, 40(sp)
    ld s6, 48(sp)
    ld s5, 56(sp)
    ld s4, 64(sp)
    ld s3, 72(sp)
    ld s2, 80(sp)
    ld s1, 88(sp)
    ld s0, 96(sp)
    ld ra, 104(sp)
    addi sp, sp, 112
    ret
LOPPU(vahdi)
# @loppu vahti

# @alku testattavat
# long kasvata_oikein(long x): käyttää s0:aa, mutta tallentaa sen.
FUNKTIO(kasvata_oikein)
    addi sp, sp, -16
    sd s0, 8(sp)
    addi s0, a0, 1
    mv a0, s0
    ld s0, 8(sp)
    addi sp, sp, 16
    ret
LOPPU(kasvata_oikein)

# long kasvata_rikki(long x): käyttää s0:aa tallentamatta sitä.
FUNKTIO(kasvata_rikki)
    addi s0, a0, 1
    mv a0, s0
    ret
LOPPU(kasvata_rikki)
# @loppu testattavat
PINO_EI_SUORITETTAVA
