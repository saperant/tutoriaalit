// Sama 32-bittinen luku isännän muistissa, verkon tavujärjestyksessä ja
// rakenteessa, jonka kääntäjä on täyttänyt tasausta varten.
#include <arpa/inet.h>
#include <stdio.h>

#include "tlv.h"

static void tavut(const char *otsikko, const void *p, size_t n) {
    const uint8_t *b = (const uint8_t *)p;
    printf("%-14s", otsikko);
    for (size_t i = 0; i < n; i++) {
        printf(" %02x", b[i]);
    }
    printf("\n");
}

// @alku rakenne
struct otsake {                          // EI näin verkkoon
    uint8_t tyyppi;
    uint32_t pituus;                     // tasataan 4:n monikertaan
};
// @loppu rakenne

int main(void) {
    // @alku jarjestys
    uint32_t x = 0x0a0b0c0d;
    tavut("muistissa:", &x, 4);   // x86-64 ja ARM64: little-endian
    uint32_t verkko = htonl(x);
    tavut("htonl:", &verkko, 4);         // big-endian
    uint8_t b[4];
    kirjoita_u32(b, x);
    tavut("kirjoita_u32:", b, 4);
    printf("lue_u32 palauttaa: 0x%08x\n", lue_u32(b));
    // @loppu jarjestys

    // @alku tayte
    struct otsake o = {.tyyppi = 1, .pituus = 5};
    printf("sizeof(struct otsake) = %zu, kenttiä yhteensä 5 tavua\n",
           sizeof o);
    // @loppu tayte
    return 0;
}
