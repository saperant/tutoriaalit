#include "funktio.h"
    .text
# @alku laske
# size_t laske(const char *s, char c)
#   rdi = s, sil = c (vain alin tavu on määritelty), paluu rax
FUNKTIO(laske)
    xor %eax, %eax              # lukumäärä
1:  movzbl (%rdi), %edx         # seuraava tavu
    test %dl, %dl
    jz 3f                       # nollatavu: loppu
    cmp %sil, %dl               # vertaa vain alinta tavua
    jne 2f
    inc %rax
2:  inc %rdi
    jmp 1b
3:  ret
LOPPU(laske)
# @loppu laske
PINO_EI_SUORITETTAVA
