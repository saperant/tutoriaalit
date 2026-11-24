# Sama RISC-V:llä.
    .globl _start
    .text
_start:
# @alku silmukka
1:  li a0, 0                    # tiedosto 0 (stdin)
    la a1, puskuri
    li a2, 64
    li a7, 63                   # järjestelmäkutsu 63 = read
    ecall
    blez a0, 4f                 # 0 = syöte loppui, < 0 = virhe
    mv a2, a0                   # write kirjoittaa luetun määrän
    mv t0, a1                   # p = puskuri
    add t1, a1, a2              # loppu
    li t4, 25
2:  lbu t2, 0(t0)
    addi t3, t2, -97            # merkki - 'a'
    bgtu t3, t4, 3f             # ei a–z (etumerkitön vertailu)
    addi t2, t2, -32
    sb t2, 0(t0)
3:  addi t0, t0, 1
    bltu t0, t1, 2b
    li a0, 1                    # tiedosto 1 (stdout)
    li a7, 64                   # järjestelmäkutsu 64 = write
    ecall                       # (a1 ja a2 ovat jo paikallaan)
    j 1b
# @loppu silmukka
4:  slt a0, a0, zero            # paluuarvo 1, jos read epäonnistui
    li a7, 93                   # järjestelmäkutsu 93 = exit
    ecall

    .bss
puskuri:
    .space 64
    .section .note.GNU-stack,"",@progbits
