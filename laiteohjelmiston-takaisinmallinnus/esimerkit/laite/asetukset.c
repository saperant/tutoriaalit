/* Asetuslohkon luku ja tarkistus. */
#include <stddef.h>
#include <string.h>

#include "asetukset.h"
#include "tarkiste.h"
#include "xtea.h"

#ifndef KORJATTU
/* Laitteen yhteinen avain huoltosalasanan purkuun. */
static const uint32_t avain[4] = {
    0x8F2A6C11u, 0x3B9D04E7u, 0xC6715AF2u, 0x1E48B903u,
};
#endif

static const asetukset_t oletukset = {
    .taikaluku = ASETUKSET_TAIKA,
    .sarjanumero = "LT100-000000",
    .kerroin = 0x10000,
    .debug_lukitus = DEBUG_AUKI,
};

const asetukset_t *asetukset(void) {
    if (!asetukset_kelpaa()) {
        return &oletukset;
    }
    return (const asetukset_t *)ASETUKSET_OSOITE;
}

int asetukset_kelpaa(void) {
    const asetukset_t *a = (const asetukset_t *)ASETUKSET_OSOITE;
    if (a->taikaluku != ASETUKSET_TAIKA ||
        a->pituus != offsetof(asetukset_t, crc32)) {
        return 0;
    }
    return crc32(a, a->pituus) == a->crc32;
}

#ifndef KORJATTU
int huoltosalasana_oikein(const char *salasana) {
    uint32_t selko[4];
    memcpy(selko, asetukset()->huoltosalasana, sizeof selko);
    xtea_pura(&selko[0], avain);
    xtea_pura(&selko[2], avain);
    int oikein = strncmp((const char *)selko, salasana, sizeof selko) == 0;
    memset(selko, 0, sizeof selko);
    return oikein;
}
#endif
