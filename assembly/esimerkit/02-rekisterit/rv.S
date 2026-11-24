    .text
# @alku lisaa32
# long lisaa32(long a, long b): 32-bittinen yhteenlasku.
    .globl lisaa32
lisaa32:
    addw a0, a0, a1             # W-käsky laajentaa etumerkillä
    ret
# @loppu lisaa32

# @alku tavu
# unsigned tavu(const uint32_t *p, long i): sanan tavu i.
    .globl tavu
tavu:
    add a0, a0, a1              # osoite p + i
    lbu a0, 0(a0)               # lue tavu, laajenna nollilla
    ret
# @loppu tavu
    .section .note.GNU-stack,"",@progbits
