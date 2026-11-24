/* SHA-512 (FIPS 180-4). Pieni, riippumaton toteutus käynnistimelle. */
#ifndef SHA512_H
#define SHA512_H

#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint64_t tila[8];
    uint64_t pituus;      /* käsiteltyjä tavuja */
    uint8_t puskuri[128];
    size_t tayttoaste;    /* puskurin tavut */
} sha512_t;

void sha512_alusta(sha512_t *s);
void sha512_lisaa(sha512_t *s, const void *data, size_t koko);
void sha512_valmis(sha512_t *s, uint8_t tiiviste[64]);

#endif
