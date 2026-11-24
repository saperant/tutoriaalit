    .text
# @alku kertoma
# long kertoma(long n): rekursio ja kutsun yli säilyvä rekisteri.
    .globl kertoma
kertoma:
    cmp $1, %rdi
    jg 1f
    mov $1, %eax                # n <= 1: 1
    ret
1:  push %rbx                   # rbx on kutsutun tallennettava
    mov %rdi, %rbx              # n talteen kutsun yli
    lea -1(%rdi), %rdi
    call kertoma                # rax = (n - 1)!
    imul %rbx, %rax             # n * (n - 1)!
    pop %rbx
    ret
# @loppu kertoma

# @alku summa9
# long summa9(long a, ..., long i): kuusi ensimmäistä argumenttia
# rekistereissä, loput pinossa paluuosoitteen yläpuolella.
    .globl summa9
summa9:
    lea (%rdi,%rsi), %rax       # a + b
    add %rdx, %rax              # + c
    add %rcx, %rax              # + d
    add %r8, %rax               # + e
    add %r9, %rax               # + f
    add 8(%rsp), %rax           # + g (7. argumentti)
    add 16(%rsp), %rax          # + h
    add 24(%rsp), %rax          # + i
    ret
# @loppu summa9

# @alku kay_lapi
# long kay_lapi(const long *t, long n, long (*f)(long)):
# kutsuu f:ää jokaiselle alkiolle ja palauttaa tulosten summan.
    .globl kay_lapi
kay_lapi:
    push %rbx                   # t
    push %r12                   # jäljellä olevien määrä
    push %r13                   # f
    push %r14                   # summa
    sub $8, %rsp                # pino 16 tavun rajalle ennen kutsuja
    mov %rdi, %rbx
    mov %rsi, %r12
    mov %rdx, %r13
    xor %r14d, %r14d
    test %r12, %r12
    jle 2f
1:  mov (%rbx), %rdi
    call *%r13                  # f(*t): saa muuttaa kutsujan rekisterejä
    add %rax, %r14
    add $8, %rbx
    dec %r12
    jnz 1b
2:  mov %r14, %rax
    add $8, %rsp
    pop %r14                    # palautus käänteisessä järjestyksessä
    pop %r13
    pop %r12
    pop %rbx
    ret
# @loppu kay_lapi
    .section .note.GNU-stack,"",@progbits
