#include "../02-rajapinta/funktio.h"
    .text
FUNKTIO(kolminkertaista)
    slli t0, a0, 1
    add a0, a0, t0
    ret
LOPPU(kolminkertaista)
PINO_EI_SUORITETTAVA
