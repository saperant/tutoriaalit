/* Laiteohjelmistokuvan otsake. Kuva = otsake (256 tavua) + sovellus.
 * Allekirjoitus kattaa otsakkeen 80 ensimmäistä tavua, ja niissä on
 * sovelluksen SHA-512-tiiviste, joten se kattaa myös sovelluksen. */
#ifndef OTSAKE_H
#define OTSAKE_H

#include <stdint.h>

#define KUVA_TAIKA 0x4B555641u        /* "AVUK" */
#define OTSAKKEEN_KOKO 256u
#define ALLEKIRJOITETTU_OSA 80u

typedef struct {
    uint32_t taika;
    uint32_t versio;                  /* versionpalautuksen esto */
    uint32_t koko;                    /* sovelluksen tavut */
    uint32_t varattu;
    uint8_t tiiviste[64];             /* SHA-512(sovellus) */
    uint8_t allekirjoitus[64];        /* Ed25519(otsake[0..80)) */
    uint8_t tayte[OTSAKKEEN_KOKO - 144];
} kuvan_otsake_t;

_Static_assert(sizeof(kuvan_otsake_t) == OTSAKKEEN_KOKO,
               "otsakkeen koko");

#endif
