# Globaali data RISC-V:llä: osoite rekisteriin la-pseudokäskyllä.

    .section .rodata
alkuluvut:
    .quad 2, 3, 5, 7, 11

    .data
    .globl laskuri
laskuri:
    .quad 100

    .bss
    .globl kutsuja
kutsuja:
    .zero 8

    .text
# @alku seuraava
# long seuraava(void)
    .globl seuraava
seuraava:
    la t0, kutsuja              # osoite: auipc + addi
    ld t1, 0(t0)                # lataa, kasvata, tallenna
    addi t1, t1, 1
    sd t1, 0(t0)
    la t0, laskuri
    ld a0, 0(t0)
    addi a0, a0, 1
    sd a0, 0(t0)
    ret
# @loppu seuraava

# @alku alkuluku
# long alkuluku(long i)
    .globl alkuluku
alkuluku:
    la t0, alkuluvut
    slli a0, a0, 3              # i * 8
    add t0, t0, a0
    ld a0, 0(t0)
    ret
# @loppu alkuluku

# @alku vakio
# unsigned long vakio(void): kokoaja purkaa li:n useaksi käskyksi.
    .globl vakio
vakio:
    li a0, 0x123456789abcdef0
    ret
# @loppu vakio
    .section .note.GNU-stack,"",@progbits
