// loki.h: verkkopalvelimen lokin analyysi kahdella toteutuksella.
#ifndef LOKI_H
#define LOKI_H

#include <stddef.h>
#include <stdint.h>

// Yhden asiakasosoitteen pyynnöt ja siirretyt tavut.
typedef struct {
    char osoite[16];        // "a.b.c.d" ja loppumerkki
    uint32_t pyynnot;
    uint64_t tavut;
} Asiakas;

typedef struct {
    Asiakas *asiakkaat;
    size_t maara;
} Yhteenveto;

// Laskee rivikohtaiset tiedot asiakkaittain. Rivit erotetaan '\n'-
// merkillä. Palauttaa asiakkaat suurimmasta pyyntömäärästä alkaen.
Yhteenveto laske_hidas(const char *loki);
Yhteenveto laske_puskuroitu(const char *loki);
Yhteenveto laske_nopea(const char *loki);

void vapauta(Yhteenveto *y);
int vertaa_asiakkaat(const void *a, const void *b);

#endif
