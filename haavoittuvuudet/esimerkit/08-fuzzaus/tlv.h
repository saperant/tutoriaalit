/* TLV-viestin jäsennin: tyyppi (1 tavu), pituus (1 tavu) ja data. */
#ifndef TLV_H
#define TLV_H

#include <stddef.h>
#include <stdint.h>

enum { TLV_NIMI = 0x03, TLV_VERSIO = 0x05, NIMI_MAX = 16 };

struct viesti {
    char nimi[NIMI_MAX];
    const char *versio;
    int tietueita;
};

/* Jäsentää viestin. Palauttaa 0 tai -1, jos viesti on virheellinen. */
int tlv_jasenna(const uint8_t *data, size_t koko, struct viesti *viesti);

#endif
