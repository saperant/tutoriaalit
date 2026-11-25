    .text
# @alku lisaa
# int lisaa_u64(uint64_t a, uint64_t b, uint64_t *tulos): kantoluku.
    .globl lisaa_u64
lisaa_u64:
    add %rsi, %rdi              # asettaa liput CF (kanto) ja OF
    mov %rdi, (%rdx)            # mov ei muuta lippuja
    setc %al                    # al = CF
    movzbl %al, %eax
    ret

# int lisaa_i64(int64_t a, int64_t b, int64_t *tulos): ylivuoto.
    .globl lisaa_i64
lisaa_i64:
    add %rsi, %rdi
    mov %rdi, (%rdx)
    seto %al                    # al = OF
    movzbl %al, %eax
    ret
# @loppu lisaa

# @alku vertaa
# long vertaa(long a, long b): -1, 0 tai 1.
    .globl vertaa
vertaa:
    xor %eax, %eax
    cmp %rsi, %rdi              # liput kuten a - b
    setg %al                    # a > b (etumerkillinen)
    setl %cl                    # a < b
    movzbl %cl, %ecx
    sub %rcx, %rax
    ret
# @loppu vertaa
    .section .note.GNU-stack,"",@progbits
