/* XTEA, 32 kierrosta (Needham ja Wheeler 1997). */
#include "xtea.h"

void xtea_pura(uint32_t lohko[2], const uint32_t avain[4]) {
    uint32_t v0 = lohko[0], v1 = lohko[1];
    const uint32_t delta = 0x9E3779B9u;
    uint32_t summa = delta * 32u;
    for (int i = 0; i < 32; i++) {
        v1 -= (((v0 << 4) ^ (v0 >> 5)) + v0) ^
              (summa + avain[(summa >> 11) & 3u]);
        summa -= delta;
        v0 -= (((v1 << 4) ^ (v1 >> 5)) + v1) ^ (summa + avain[summa & 3u]);
    }
    lohko[0] = v0;
    lohko[1] = v1;
}
