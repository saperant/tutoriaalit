#include <inttypes.h>
#include <stdio.h>

#include "bitit.h"

int main(void) {
    uint64_t x = 0x0123456789ABCDEFu;
    printf("ykkosia(%#" PRIx64 ") = %d\n", x, ykkosia(x));
    printf("nollia_lopussa(0x50) = %d\n", nollia_lopussa(0x50));
    printf("nollia_lopussa(0) = %d\n", nollia_lopussa(0));
    printf("kaanna(%#" PRIx64 ") = %#" PRIx64 "\n", x, kaanna(x));
    int q = 0;
    int r = jaa_turvallisesti(84, 2, &q);
    printf("jaa_turvallisesti(84, 2) = %d, tulos %d\n", r, q);
    printf("jaa_turvallisesti(1, 0) = %d\n", jaa_turvallisesti(1, 0, &q));
    return 0;
}
