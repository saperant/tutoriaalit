    .text
    .globl    kymmenesosa
kymmenesosa:
    movabsq    $-3689348814741910323, %rax
    mulq    %rdi
    movq    %rdx, %rax
    shrq    $3, %rax
    ret
    .globl    kahdeksasosa
kahdeksasosa:
    testq    %rdi, %rdi
    leaq    7(%rdi), %rax
    cmovns    %rdi, %rax
    sarq    $3, %rax
    ret
