// Roofline-malli: laskentaintensiteetti ja saavutettava suorituskyky.
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>

#include "mittari.h"

// @alku malli
typedef struct {
    const char *nimi;
    double laskuja;     // liukulukuoperaatioita
    double tavuja;      // muistiliikennettä samassa työssä
} Ydin;

// Saavutettava teho (GFLOP/s) on pienempi kahdesta katosta:
// laskentahuippu tai kaistanleveys kertaa intensiteetti.
static double katto(double huippu, double kaista, double intensiteetti)
{
    double muisti = kaista * intensiteetti;
    return muisti < huippu ? muisti : huippu;
}
// @loppu malli

static void tulosta_malli(double huippu, double kaista)
{
    // @alku ytimet
    // Yksi alkio, kahdeksan tavun double-luvut. Kirjoitettava rivi
    // luetaan ensin välimuistiin (write-allocate): kirjoitus maksaa 16 B.
    // Matriisitulon luvut ovat koko laskennalle: 2n^3 laskua ja
    // ihanteellisesti kolmen n x n -matriisin siirto kerran.
    const double n = 1024;
    const Ydin ytimet[] = {
        {"kopio a[i] = b[i]", 0, 24},
        {"triad a[i] = b[i] + s*c[i]", 2, 32},
        {"pistetulo s += a[i]*b[i]", 2, 16},
        {"polynomi aste 16, y = p(x)", 32, 24},
        {"matriisitulo n = 1024", 2 * n * n * n, 3 * n * n * 8},
    };
    // @loppu ytimet
    printf("huippu %.1f GFLOP/s, kaista %.1f GB/s, harjanne %.2f F/B\n",
           huippu, kaista, huippu / kaista);
    printf("%-28s %8s %10s %s\n", "ydin", "F/B", "GFLOP/s", "raja");
    for (size_t i = 0; i < sizeof ytimet / sizeof ytimet[0]; i++) {
        double in = ytimet[i].laskuja / ytimet[i].tavuja;
        double k = katto(huippu, kaista, in);
        printf("%-28s %8.3f %10.2f %s\n", ytimet[i].nimi, in, k,
               k < huippu ? "muisti" : "laskenta");
    }
}

enum { N = 1 << 23 };    // 64 MiB / taulukko

typedef struct {
    double *a, *b, *c;
} Taulukot;

// @alku triad
static void triad(void *p)
{
    Taulukot *t = p;
    for (size_t i = 0; i < N; i++) {
        t->a[i] = t->b[i] + 3.0 * t->c[i];
    }
    kayta(t->a);
}
// @loppu triad

// Kahdeksan riippumatonta kertolasku-yhteenlaskuketjua rekistereissä.
static void laskenta(void *p)
{
    double *tulos = p;
    double x[8] = {1, 2, 3, 4, 5, 6, 7, 8};
    for (int k = 0; k < 1 << 24; k++) {
        for (int j = 0; j < 8; j++) {
            x[j] = x[j] * 0.999999 + 0.000001;
        }
    }
    *tulos = x[0] + x[7];
    kayta(tulos);
}

int main(int argc, char **argv)
{
    if (!mittaustila(argc, argv)) {
        printf("esimerkkikone\n");
        tulosta_malli(100.0, 20.0);
        return 0;
    }
    Taulukot t = {malloc(N * sizeof(double)), malloc(N * sizeof(double)),
                  malloc(N * sizeof(double))};
    if (!t.a || !t.b || !t.c) {
        return EXIT_FAILURE;
    }
    for (size_t i = 0; i < N; i++) {
        t.a[i] = 0;
        t.b[i] = 1;
        t.c[i] = 2;
    }
    Tilasto ta = mittaa(triad, &t, 11);
    double kaista = 32.0 * N / (ta.mediaani * 1e6);
    double tulos;
    Tilasto tl = mittaa(laskenta, &tulos, 5);
    double huippu = 2.0 * 8 * (1 << 24) / (tl.mediaani * 1e6);
    printf("mitattu kone (yksi ydin, skalaarikoodi)\n");
    tulosta_malli(huippu, kaista);
    free(t.a);
    free(t.b);
    free(t.c);
    return 0;
}
