# Samat funktiot RISC-V:llä. Kokoaja käyttää 16-bittisiä tiivistettyjä
# käskyjä (C-laajennus) aina kun se on mahdollista.
    .text
    .globl kaksinkertaista
kaksinkertaista:                # long kaksinkertaista(long x)
    add a0, a0, a0              # a0 = x + x
    ret

    .globl summaa
summaa:                         # long summaa(long a, long b)
    add a0, a0, a1
    ret

    .globl summaa_pitka
summaa_pitka:                   # sama ilman tiivistettyjä käskyjä
    .option push
    .option norvc
    add a0, a0, a1
    ret
    .option pop
    .section .note.GNU-stack,"",@progbits
