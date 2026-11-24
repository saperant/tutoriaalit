/* Laitekohtaiset asetukset flashin lopussa (0x3F000). Tehdas kirjoittaa
 * lohkon; sovellus vain lukee sitä. */
#ifndef ASETUKSET_H
#define ASETUKSET_H

#include <stdint.h>

#define ASETUKSET_OSOITE   0x0003F000u
#define ASETUKSET_TAIKA    0x54455341u /* "ASET" */
#define DEBUG_AUKI         0xFFFFFFFFu /* tyhjä flash: portti auki */

typedef struct {
    uint32_t taikaluku;
    uint16_t versio;
    uint16_t pituus;          /* tarkisteen kattama pituus */
    char sarjanumero[12];
    int32_t kerroin;          /* kalibrointi, Q16.16 */
    int32_t siirto;           /* kalibrointi, sadasosa-asteina */
    uint32_t debug_lukitus;   /* DEBUG_AUKI tai lukitustaso */
    uint32_t huoltosalasana[4]; /* XTEA-salattu, 16 tavua */
    uint32_t crc32;           /* edellisten kenttien tarkiste */
} asetukset_t;

const asetukset_t *asetukset(void);
int asetukset_kelpaa(void);
int huoltosalasana_oikein(const char *salasana);

#endif
