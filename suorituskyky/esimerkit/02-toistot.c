// Toistomittaus: miksi mediaani eikä keskiarvo.
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>

#include "mittari.h"

static double keskiarvo(const double *x, size_t n)
{
    double s = 0;
    for (size_t i = 0; i < n; i++) {
        s += x[i];
    }
    return s / (double)n;
}

enum { N = 1 << 20 };

typedef struct {
    int *taulukko;
    int64_t summa;
} Tila;

static void summaa(void *p)
{
    Tila *t = p;
    int64_t s = 0;
    for (size_t i = 0; i < N; i++) {
        s += t->taulukko[i];
    }
    t->summa = s;
    kayta(&t->summa);
}

// @alku kylma
static void mittaa_kaikki(void)
{
    Tila t = {malloc(N * sizeof(int)), 0};
    if (t.taulukko == NULL) {
        exit(EXIT_FAILURE);
    }
    for (size_t i = 0; i < N; i++) {
        t.taulukko[i] = (int)(i % 1000);
    }
    // Toinen suuri taulukko syrjäyttää ensimmäisen välimuisteista.
    size_t m = 64u << 20;
    char *muu = malloc(m);
    if (muu == NULL) {
        exit(EXIT_FAILURE);
    }
    memset(muu, 1, m);
    kayta(muu);
    // Ensimmäinen kutsu: data ei ole välimuisteissa.
    int64_t alku = seinakello_ns();
    summaa(&t);
    double kylma = (double)(seinakello_ns() - alku) / 1e6;

    double naytteet[51];
    for (int i = 0; i < 51; i++) {
        alku = seinakello_ns();
        summaa(&t);
        naytteet[i] = (double)(seinakello_ns() - alku) / 1e6;
    }
    double ka = keskiarvo(naytteet, 51);
    Tilasto s = laske_tilasto(naytteet, 51);
    printf("taulukon summa, 4 MiB, 51 toistoa (ms)\n");
    printf("  ensimmainen ajo  %8.3f\n", kylma);
    printf("  pienin           %8.3f\n", s.pienin);
    printf("  mediaani         %8.3f  (MAD %.3f)\n", s.mediaani, s.mad);
    printf("  keskiarvo        %8.3f\n", ka);
    printf("  suurin           %8.3f\n", s.suurin);
    free(muu);
    free(t.taulukko);
}
// @loppu kylma

int main(int argc, char **argv)
{
    if (mittaustila(argc, argv)) {
        mittaa_kaikki();
        return 0;
    }
    // @alku testi
    // Yksitoista mittausta (ms), joista yksi osui keskeytyksen kohdalle.
    double ajat[] = {10.2, 10.1, 10.3, 10.2, 31.7, 10.2,
                     10.4, 10.1, 10.2, 10.3, 10.2};
    size_t n = sizeof ajat / sizeof ajat[0];
    printf("keskiarvo %.2f ms\n", keskiarvo(ajat, n));
    Tilasto t = laske_tilasto(ajat, n);
    printf("mediaani  %.2f ms\n", t.mediaani);
    printf("pienin    %.2f ms\n", t.pienin);
    printf("suurin    %.2f ms\n", t.suurin);
    printf("MAD       %.2f ms\n", t.mad);
    // @loppu testi
    return 0;
}
