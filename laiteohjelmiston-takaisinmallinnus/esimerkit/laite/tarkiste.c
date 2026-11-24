/* Tarkisteet. CRC-32 lasketaan taulukolla, joka muodostetaan
 * ensimmäisellä kutsulla; CRC-16 bitti kerrallaan. */
#include "tarkiste.h"

static uint32_t taulukko[256];
static int taulukko_valmis;

static void muodosta_taulukko(void) {
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t c = i;
        for (int k = 0; k < 8; k++) {
            c = (c & 1u) ? 0xEDB88320u ^ (c >> 1) : c >> 1;
        }
        taulukko[i] = c;
    }
    taulukko_valmis = 1;
}

uint32_t crc32(const void *data, size_t pituus) {
    if (!taulukko_valmis) {
        muodosta_taulukko();
    }
    const uint8_t *p = data;
    uint32_t c = 0xFFFFFFFFu;
    while (pituus-- > 0) {
        c = taulukko[(c ^ *p++) & 0xFFu] ^ (c >> 8);
    }
    return c ^ 0xFFFFFFFFu;
}

uint16_t crc16_ccitt(const uint8_t *data, size_t pituus) {
    uint16_t c = 0xFFFFu;
    while (pituus-- > 0) {
        c ^= (uint16_t)(*data++ << 8);
        for (int k = 0; k < 8; k++) {
            c = (c & 0x8000u) ? (uint16_t)((c << 1) ^ 0x1021u)
                              : (uint16_t)(c << 1);
        }
    }
    return c;
}
