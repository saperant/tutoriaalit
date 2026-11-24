/* Jaksolliset tehtävät: laskenta-aika C, jakso T (= määräaika D) ja
 * prioriteetti nopeusmonotonisesti (lyhin jakso tärkein). Muunnelma
 * 14-rms-ylikuorma (-DYLIKUORMA) pidentää T3:n laskenta-aikaa. */
#ifndef JOUKKO_H
#define JOUKKO_H

#include "kide.h"

// @alku joukko
typedef struct {
    const char *nimi;
    TickType_t c;          /* pahin laskenta-aika (WCET) tikkeinä */
    TickType_t t;          /* jakso ja määräaika */
    UBaseType_t prio;
} jaksollinen_t;

static const jaksollinen_t joukko[] = {
    {"T1", 1, 4, 3},
    {"T2", 2, 6, 2},
#ifdef YLIKUORMA
    {"T3", 4, 10, 1},
#else
    {"T3", 3, 12, 1},
#endif
};
#define TEHTAVIA (sizeof joukko / sizeof joukko[0])
// @loppu joukko

/* Vasteaika-analyysi (analyysi.c): palauttaa pahimman vasteajan tai
 * 0, jos se ylittää määräajan. Tulostaa iteraation vaiheet. */
TickType_t vasteaika(unsigned i);
/* Käyttöaste tuhannesosina ja Liu–Laylandin raja n tehtävälle. */
unsigned kayttoaste_promille(void);
unsigned ll_raja_promille(unsigned n);

#endif
