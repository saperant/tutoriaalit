    .text
# @alku pituus
# size_t pituus(const char *s): merkkijonon pituus (strlen).
    .globl pituus
pituus:
    mv t0, a0                   # p = s
1:  lbu t1, 0(t0)
    beqz t1, 2f                 # *p == 0?
    addi t0, t0, 1              # p++
    j 1b
2:  sub a0, t0, a0              # p - s
    ret
# @loppu pituus

# @alku rajaa
# long rajaa(long x, long ala, long yla): x rajattuna väliin.
    .globl rajaa
rajaa:
    bge a0, a1, 1f              # x >= ala: ohita
    mv a0, a1
1:  ble a0, a2, 2f              # x <= yla: ohita
    mv a0, a2
2:  ret
# @loppu rajaa
    .section .note.GNU-stack,"",@progbits
