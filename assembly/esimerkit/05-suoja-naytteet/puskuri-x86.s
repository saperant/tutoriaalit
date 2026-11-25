    .text
    .globl    ensimmainen
ensimmainen:
    subq    $40, %rsp
    movl    $24, %esi
    movq    %fs:40, %rdi
    movq    %rdi, 24(%rsp)
    movq    %rsp, %rdi
    call    tayta@PLT
    movsbq    (%rsp), %rax
    movq    24(%rsp), %rdx
    subq    %fs:40, %rdx
    jne    .L5
    addq    $40, %rsp
    ret
.L5:
    call    __stack_chk_fail@PLT
