    .text
# @alku lajittele
# void lajittele(long *t, long n): lisäyslajittelu.
    .globl lajittele
lajittele:
    mov $1, %ecx                # i = 1
1:  cmp %rsi, %rcx
    jge 4f                      # i >= n: valmis
    mov (%rdi,%rcx,8), %rax     # x = t[i]
    mov %rcx, %rdx              # j = i
2:  test %rdx, %rdx
    jz 3f                       # j == 0
    mov -8(%rdi,%rdx,8), %r8    # t[j - 1]
    cmp %rax, %r8
    jle 3f                      # t[j - 1] <= x: paikka löytyi
    mov %r8, (%rdi,%rdx,8)      # t[j] = t[j - 1]
    dec %rdx
    jmp 2b
3:  mov %rax, (%rdi,%rdx,8)     # t[j] = x
    inc %rcx
    jmp 1b
4:  ret
# @loppu lajittele
    .globl lajittele_loppu
lajittele_loppu:
    .section .note.GNU-stack,"",@progbits
