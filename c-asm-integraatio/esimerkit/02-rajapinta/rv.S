#include "funktio.h"
    .text
# @alku laske
# size_t laske(const char *s, char c)
#   a0 = s, a1 = c (laajennettu tyypin mukaan), paluu a0
FUNKTIO(laske)
    li t0, 0                    # lukumäärä
1:  lbu t1, 0(a0)               # seuraava tavu etumerkittömänä
    beqz t1, 3f                 # nollatavu: loppu
    bne t1, a1, 2f
    addi t0, t0, 1
2:  addi a0, a0, 1
    j 1b
3:  mv a0, t0
    ret
LOPPU(laske)
# @loppu laske
PINO_EI_SUORITETTAVA
