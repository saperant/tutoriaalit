# Sama ohjelma RISC-V:llä (RV64, Linux).
# @alku ohjelma
    .section .rodata            # data ensin: li tarvitsee pituuden
viesti:                         # arvon jo kootessaan
    .ascii "Hei, konekieli!\n"
    .set pituus, . - viesti

    .globl _start
    .text
_start:
    li a0, 1                    # 1. argumentti: tiedosto 1 (stdout)
    la a1, viesti               # 2. argumentti: puskurin osoite
    li a2, pituus               # 3. argumentti: tavujen määrä
    li a7, 64                   # järjestelmäkutsu 64 = write
    ecall
    li a0, 0                    # paluuarvo 0
    li a7, 93                   # järjestelmäkutsu 93 = exit
    ecall
# @loppu ohjelma
    .section .note.GNU-stack,"",@progbits
