/* ARM semihosting: SYS_WRITE0 (0x04) ja SYS_EXIT_EXTENDED (0x20). */
#include "semihost.h"

static int kutsu(int op, const void *arg) {
    register int r0 __asm__("r0") = op;
    register const void *r1 __asm__("r1") = arg;
    __asm__ volatile("bkpt 0xab" : "+r"(r0) : "r"(r1) : "memory");
    return r0;
}

void tulosta(const char *teksti) {
    kutsu(0x04, teksti);
}

void tulosta_luku(uint32_t luku) {
    char puskuri[11];
    int i = 10;
    puskuri[i] = '\0';
    do {
        puskuri[--i] = (char)('0' + luku % 10);
        luku /= 10;
    } while (luku > 0);
    tulosta(&puskuri[i]);
}

_Noreturn void lopeta(int koodi) {
    /* ADP_Stopped_ApplicationExit ja paluuarvo. */
    const uint32_t lohko[2] = {0x20026u, (uint32_t)koodi};
    kutsu(0x20, lohko);
    for (;;) {
    }
}
