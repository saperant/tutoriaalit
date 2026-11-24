    .text
# @alku lisaa
# RISC-V:ssä ei ole lippurekisteriä: kanto ja ylivuoto lasketaan.
    .globl lisaa_u64
lisaa_u64:
    add t0, a0, a1
    sd t0, 0(a2)
    sltu a0, t0, a0             # kanto, jos tulos < a
    ret

    .globl lisaa_i64
lisaa_i64:
    add t0, a0, a1
    sd t0, 0(a2)
    xor t1, a0, t0              # etumerkki muuttui a:sta tulokseen?
    xor t2, a1, t0              # ja b:stä tulokseen?
    and t1, t1, t2
    srli a0, t1, 63             # ylivuoto, jos molemmat muuttuivat
    ret
# @loppu lisaa

# @alku vertaa
# long vertaa(long a, long b): -1, 0 tai 1.
    .globl vertaa
vertaa:
    slt t0, a1, a0              # a > b
    slt t1, a0, a1              # a < b
    sub a0, t0, t1
    ret
# @loppu vertaa
    .section .note.GNU-stack,"",@progbits
