# uint32_t adler32(const uint8_t *data, size_t n)
    .text
    .globl adler32
adler32:
    li t0, 1                    # a = 1
    li t1, 0                    # b = 0
    li t2, 65521                # MOD
    add a1, a0, a1              # loppu = data + n
1:  bgeu a0, a1, 2f
    lbu t3, 0(a0)
    add t0, t0, t3
    remu t0, t0, t2             # a = (a + tavu) % MOD
    add t1, t1, t0
    remu t1, t1, t2             # b = (b + a) % MOD
    addi a0, a0, 1
    j 1b
2:  slli a0, t1, 16
    or a0, a0, t0
    sext.w a0, a0               # psABI: 32-bittinen paluuarvo
    ret                         # etumerkkilaajennettuna
    .section .note.GNU-stack,"",@progbits
