#include "../01-rajapinta/funktio.h"
    .text
# @alku vahti
# long vahdi(long (*f)(long), long x, unsigned *muuttuneet)
# Täyttää kutsun yli säilyvät rekisterit tunnetuilla arvoilla, kutsuu
# f(x) ja kirjaa bitteinä, mitkä f muutti: 0 = rbx, 1 = rbp,
# 2–5 = r12–r15. Palauttaa f:n paluuarvon.
.macro tarkista rek, arvo, bitti
    movabs $\arvo, %rdx
    cmp %rdx, \rek
    je 9f
    or $(1 << \bitti), %ecx
9:
.endm

FUNKTIO(vahdi)
    push %rbx                   # vahti itse noudattaa sopimusta
    push %rbp
    push %r12
    push %r13
    push %r14
    push %r15
    push %rdx                   # muuttuneet; pino samalla 16:n rajalle
    movabs $0x1111111111111111, %rbx
    movabs $0x2222222222222222, %rbp
    movabs $0x3333333333333333, %r12
    movabs $0x4444444444444444, %r13
    movabs $0x5555555555555555, %r14
    movabs $0x6666666666666666, %r15
    mov %rdi, %rax
    mov %rsi, %rdi
    call *%rax                  # rax = f(x)
    xor %ecx, %ecx
    tarkista %rbx, 0x1111111111111111, 0
    tarkista %rbp, 0x2222222222222222, 1
    tarkista %r12, 0x3333333333333333, 2
    tarkista %r13, 0x4444444444444444, 3
    tarkista %r14, 0x5555555555555555, 4
    tarkista %r15, 0x6666666666666666, 5
    pop %rdx
    mov %ecx, (%rdx)
    pop %r15
    pop %r14
    pop %r13
    pop %r12
    pop %rbp
    pop %rbx
    ret
LOPPU(vahdi)
# @loppu vahti

# @alku testattavat
# long kasvata_oikein(long x): käyttää rbx:ää, mutta tallentaa sen.
FUNKTIO(kasvata_oikein)
    push %rbx
    lea 1(%rdi), %rbx
    mov %rbx, %rax
    pop %rbx
    ret
LOPPU(kasvata_oikein)

# long kasvata_rikki(long x): käyttää rbx:ää tallentamatta sitä.
FUNKTIO(kasvata_rikki)
    lea 1(%rdi), %rbx
    mov %rbx, %rax
    ret
LOPPU(kasvata_rikki)
# @loppu testattavat

# @alku tasaamatta
# void kutsu_tasaamatta(void (*f)(void)): kutsuu f:ää korjaamatta pinon
# tasausta. Paluuosoite on vienyt pinosta 8 tavua, joten f saa pinon,
# joka on 8 tavua sivussa sopimuksen lupaamasta.
FUNKTIO(kutsu_tasaamatta)
    call *%rdi
    ret
LOPPU(kutsu_tasaamatta)
# @loppu tasaamatta
PINO_EI_SUORITETTAVA
