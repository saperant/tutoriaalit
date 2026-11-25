# Miten globaalin datan osoitus ja vakiot koodataan (RISC-V).
    .data
luku:
    .quad 7
    .text
osoitus:
    lla a1, luku                # auipc + addi, linkkeri täyttää
    la a2, luku                 # PIC-koodissa GOT:n kautta: auipc + ld
    li a0, 5                    # mahtuu 12 bittiin: yksi käsky
    li a0, 0x12345              # lui + addi
    li a0, 0x123456789abcdef0   # 64 bittiä: käskyjen ketju
    ret
    .section .note.GNU-stack,"",@progbits
