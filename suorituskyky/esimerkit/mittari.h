// mittari.h: kellot, toistomittaus ja tulosten tilastot.
//
// Esimerkit toimivat kahdessa tilassa. Ilman argumentteja ne ajavat
// toiminnallisen testin pienellä syötteellä ja tulostavat vain
// deterministisiä tuloksia. Argumentilla --mittaa ne mittaavat
// optimoidulla käännöksellä suuremmalla syötteellä (ks. Makefile).
#ifndef MITTARI_H
#define MITTARI_H

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// @alku kellot
// Seinäkello: monotoninen, ei hyppää kellonajan säätöjen mukana.
static inline int64_t seinakello_ns(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (int64_t)t.tv_sec * 1000000000 + t.tv_nsec;
}

// Prosessiaika: suorittimella kulunut aika kaikissa säikeissä.
static inline int64_t prosessiaika_ns(void)
{
    struct timespec t;
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &t);
    return (int64_t)t.tv_sec * 1000000000 + t.tv_nsec;
}
// @loppu kellot

// @alku kayta
// Kertoo kääntäjälle, että osoitettua muistia luetaan. Tyhjä
// asm-lause ei tuota käskyjä, mutta "memory"-merkintä estää poistamasta
// laskentaa, jonka tulos muuten jäisi käyttämättä.
static inline void kayta(const void *p)
{
    __asm__ volatile("" : : "r"(p) : "memory");
}
// @loppu kayta

// @alku tilasto
typedef struct {
    double pienin;
    double mediaani;
    double suurin;
    double mad;     // mediaanin absoluuttinen poikkeama
} Tilasto;

static inline int vertaa_double(const void *a, const void *b)
{
    double x = *(const double *)a;
    double y = *(const double *)b;
    return (x > y) - (x < y);
}

static inline double mediaani_jarjestetty(const double *x, size_t n)
{
    return n % 2 ? x[n / 2] : (x[n / 2 - 1] + x[n / 2]) / 2.0;
}

// Laskee tilaston näytteistä. Järjestää taulukon paikallaan.
static inline Tilasto laske_tilasto(double *naytteet, size_t n)
{
    qsort(naytteet, n, sizeof *naytteet, vertaa_double);
    Tilasto t = {naytteet[0], mediaani_jarjestetty(naytteet, n),
                 naytteet[n - 1], 0.0};
    double *poikkeamat = malloc(n * sizeof *poikkeamat);
    if (poikkeamat == NULL) {
        return t;
    }
    for (size_t i = 0; i < n; i++) {
        double d = naytteet[i] - t.mediaani;
        poikkeamat[i] = d < 0 ? -d : d;
    }
    qsort(poikkeamat, n, sizeof *poikkeamat, vertaa_double);
    t.mad = mediaani_jarjestetty(poikkeamat, n);
    free(poikkeamat);
    return t;
}
// @loppu tilasto

// @alku mittaa
typedef void (*Mitattava)(void *tila);

enum { MAKS_TOISTOT = 1001 };

// Ajaa funktion kerran lämmittelyksi ja sitten `toistot` kertaa.
// Palauttaa kutsujen keston tilaston millisekunteina.
static inline Tilasto mittaa(Mitattava f, void *tila, int toistot)
{
    static double naytteet[MAKS_TOISTOT];
    if (toistot < 1 || toistot > MAKS_TOISTOT) {
        fprintf(stderr, "mittaa: toistoja oltava 1-%d\n", MAKS_TOISTOT);
        exit(EXIT_FAILURE);
    }
    f(tila);                                // lämmittely
    for (int i = 0; i < toistot; i++) {
        int64_t alku = seinakello_ns();
        f(tila);
        naytteet[i] = (double)(seinakello_ns() - alku) / 1e6;
    }
    return laske_tilasto(naytteet, (size_t)toistot);
}
// @loppu mittaa

// Tulostaa mittausrivin: nimi, mediaani, hajonta (MAD) ja suhde
// vertailuaikaan, jos se on annettu.
static inline void tulosta_mittaus(const char *nimi, Tilasto t,
                                   double vertailu_ms)
{
    printf("  %-24s %10.3f ms +-%7.3f", nimi, t.mediaani, t.mad);
    if (vertailu_ms > 0 && t.mediaani > 0) {
        double s = vertailu_ms / t.mediaani;
        if (s > 0.95 && s < 1.05) {
            printf("  yhta nopea");
        } else {
            printf(s >= 1 ? "  %.1f x nopeampi" : "  %.1f x hitaampi",
                   s >= 1 ? s : 1 / s);
        }
    }
    printf("\n");
}

static inline bool mittaustila(int argc, char **argv)
{
    return argc > 1 && strcmp(argv[1], "--mittaa") == 0;
}

#endif
