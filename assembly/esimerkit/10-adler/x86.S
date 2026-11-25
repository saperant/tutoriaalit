# uint32_t adler32(const uint8_t *data, size_t n): Adler-32-tarkistussumma
# (RFC 1950): a = 1 + tavujen summa, b = a-arvojen summa, mod 65521.
    .text
    .globl adler32
adler32:
    mov $1, %r8d                # a = 1
    xor %r9d, %r9d              # b = 0
    mov $65521, %r10d           # MOD
    xor %ecx, %ecx              # i = 0
1:  cmp %rsi, %rcx
    jae 2f
    movzbl (%rdi,%rcx), %eax
    add %r8d, %eax              # a + tavu
    xor %edx, %edx
    div %r10d                   # edx:eax / MOD, jakojäännös edx:ään
    mov %edx, %r8d              # a = (a + tavu) % MOD
    lea (%r9,%r8), %eax         # b + a
    xor %edx, %edx
    div %r10d
    mov %edx, %r9d              # b = (b + a) % MOD
    inc %rcx
    jmp 1b
2:  mov %r9d, %eax
    shl $16, %eax               # (b << 16) | a
    or %r8d, %eax
    ret
    .section .note.GNU-stack,"",@progbits
