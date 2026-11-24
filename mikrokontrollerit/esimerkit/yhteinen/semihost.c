/* ARM semihosting: bkpt 0xab ja SYS_EXIT_EXTENDED (0x20).
 * Oikeassa laitteessa ilman debuggeria bkpt pysäyttää ohjelman
 * HardFaultiin, joten semihostingia käytetään vain testeissä. */
#include <stdint.h>

#include "semihost.h"

_Noreturn void lopeta(int koodi) {
    /* ADP_Stopped_ApplicationExit ja paluuarvo. */
    const uint32_t lohko[2] = {0x20026u, (uint32_t)koodi};
    register uint32_t r0 __asm__("r0") = 0x20u;
    register const uint32_t *r1 __asm__("r1") = lohko;
    __asm__ volatile("bkpt 0xab" : "+r"(r0) : "r"(r1) : "memory");
    for (;;) {
    }
}
