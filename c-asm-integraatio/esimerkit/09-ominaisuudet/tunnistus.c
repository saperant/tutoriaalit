// Prosessorin ominaisuuksien tunnistus ajonaikaisesti.
#include <stdint.h>

#include "tunnistus.h"

// @alku cpuid
static void cpuid(uint32_t lehti, uint32_t ala, uint32_t r[4]) {
    __asm__("cpuid"
            : "=a"(r[0]), "=b"(r[1]), "=c"(r[2]), "=d"(r[3])
            : "a"(lehti), "c"(ala));
}

// AVX2:n käyttö vaatii kolme asiaa: prosessori tukee AVX:ää ja AVX2:ta,
// ja käyttöjärjestelmä tallentaa 256-bittiset ymm-rekisterit
// säikeenvaihdossa (XCR0:n bitit 1 ja 2, luetaan xgetbv-käskyllä).
int avx2_kaytettavissa(void) {
    uint32_t r[4];
    cpuid(0, 0, r);
    if (r[0] < 7) {
        return 0; // lehteä 7 ei ole
    }
    cpuid(1, 0, r);
    int osxsave = (r[2] >> 27) & 1, avx = (r[2] >> 28) & 1;
    if (!osxsave || !avx) {
        return 0;
    }
    uint32_t xcr0_ala, xcr0_yla;
    __asm__("xgetbv" : "=a"(xcr0_ala), "=d"(xcr0_yla) : "c"(0));
    if ((xcr0_ala & 6) != 6) {
        return 0; // käyttöjärjestelmä ei tallenna ymm-rekistereitä
    }
    cpuid(7, 0, r);
    return (r[1] >> 5) & 1; // EBX:n bitti 5 = AVX2
}
// @loppu cpuid
