#include "../02-rajapinta/funktio.h"
    .text
# @alku kutsu
# long kutsu_kautta(long (*f)(long), long x): kutsuu f(x).
# CFI-direktiivit kertovat purkajalle, missä paluuosoite ja tallennetut
# rekisterit ovat kunkin käskyn kohdalla.
FUNKTIO(kutsu_kautta)
    CFI_ALKU
    push %rbx                   # pino 16 tavun rajalle kutsua varten
    PURKU(.cfi_def_cfa_offset 16)
    PURKU(.cfi_offset %rbx, -16)
    mov %rdi, %rax
    mov %rsi, %rdi
    call *%rax
    pop %rbx
    PURKU(.cfi_def_cfa_offset 8)
    ret
    CFI_LOPPU
LOPPU(kutsu_kautta)
# @loppu kutsu
PINO_EI_SUORITETTAVA
