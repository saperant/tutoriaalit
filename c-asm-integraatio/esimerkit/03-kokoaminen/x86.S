#include "../01-rajapinta/funktio.h"
    .text
FUNKTIO(kolminkertaista)
    lea (%rdi,%rdi,2), %rax
    ret
LOPPU(kolminkertaista)
PINO_EI_SUORITETTAVA
