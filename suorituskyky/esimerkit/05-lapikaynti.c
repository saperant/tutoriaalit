// Matriisin läpikäynti riveittäin ja sarakkeittain.
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>

#include "mittari.h"

// Matriisi on tallennettu riveittäin: alkio (i, j) on kohdassa i*n + j.
// @alku summat
[[gnu::noinline]] static double summa_riveittain(const double *m,
                                                 size_t n)
{
    double s = 0;
    for (size_t i = 0; i < n; i++) {
        for (size_t j = 0; j < n; j++) {
            s += m[i * n + j];      // peräkkäiset osoitteet
        }
    }
    return s;
}

[[gnu::noinline]] static double summa_sarakkeittain(const double *m,
                                                    size_t n)
{
    double s = 0;
    for (size_t j = 0; j < n; j++) {
        for (size_t i = 0; i < n; i++) {
            s += m[i * n + j];      // askel n * 8 tavua
        }
    }
    return s;
}
// @loppu summat

typedef struct {
    const double *m;
    size_t n;
    double tulos;
    double (*summa)(const double *, size_t);
} Tila;

static void aja(void *p)
{
    Tila *t = p;
    t->tulos = t->summa(t->m, t->n);
    kayta(&t->tulos);
}

static double *luo(size_t n)
{
    double *m = malloc(n * n * sizeof *m);
    if (m == NULL) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }
    // Pienet kokonaisluvut: summa on tarkka järjestyksestä riippumatta.
    for (size_t i = 0; i < n * n; i++) {
        m[i] = (double)(i % 7);
    }
    return m;
}

int main(int argc, char **argv)
{
    // --kerran N: kumpikin summa kerran (Cachegrindia varten)
    if (argc == 3 && strcmp(argv[1], "--kerran") == 0) {
        size_t n = strtoul(argv[2], NULL, 10);
        double *m = luo(n);
        printf("%.0f %.0f\n", summa_riveittain(m, n),
               summa_sarakkeittain(m, n));
        free(m);
        return 0;
    }
    if (mittaustila(argc, argv)) {
        printf("matriisin summa, double, n x n\n");
        for (size_t n = 256; n <= 4096; n *= 4) {
            double *m = luo(n);
            Tila r = {m, n, 0, summa_riveittain};
            Tila s = {m, n, 0, summa_sarakkeittain};
            Tilasto tr = mittaa(aja, &r, 7);
            Tilasto ts = mittaa(aja, &s, 7);
            printf(" n = %zu (%zu KiB)\n", n, n * n * 8 / 1024);
            tulosta_mittaus("riveittain", tr, 0);
            tulosta_mittaus("sarakkeittain", ts, tr.mediaani);
            free(m);
        }
        return 0;
    }
    double *m = luo(300);
    printf("riveittain    %.0f\n", summa_riveittain(m, 300));
    printf("sarakkeittain %.0f\n", summa_sarakkeittain(m, 300));
    free(m);
    return 0;
}
