#include "../02-rajapinta/funktio.h"
    .text
# @alku kutsu
# long kutsu_kautta(long (*f)(long), long x): kutsuu f(x).
FUNKTIO(kutsu_kautta)
    CFI_ALKU
    addi sp, sp, -16
    PURKU(.cfi_def_cfa_offset 16)
    sd ra, 8(sp)
    PURKU(.cfi_offset ra, -8)
    mv t0, a0
    mv a0, a1
    jalr t0
    ld ra, 8(sp)
    PURKU(.cfi_restore ra)
    addi sp, sp, 16
    PURKU(.cfi_def_cfa_offset 0)
    ret
    CFI_LOPPU
LOPPU(kutsu_kautta)
# @loppu kutsu
PINO_EI_SUORITETTAVA
