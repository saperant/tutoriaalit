// Matriisitulo kolmella silmukkajärjestyksellä ja lohkottuna.
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>

#include "mittari.h"
#include "satunnainen.h"

// Kaikki matriisit n x n, riveittäin; c = a * b.

// @alku ijk
[[gnu::noinline]] static void tulo_ijk(const double *a, const double *b,
                                       double *c, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        for (size_t j = 0; j < n; j++) {
            double s = 0;
            for (size_t k = 0; k < n; k++) {
                s += a[i * n + k] * b[k * n + j];   // b sarakkeittain
            }
            c[i * n + j] = s;
        }
    }
}
// @loppu ijk

// @alku ikj
[[gnu::noinline]] static void tulo_ikj(const double *a, const double *b,
                                       double *restrict c, size_t n)
{
    for (size_t i = 0; i < n * n; i++) {
        c[i] = 0;
    }
    for (size_t i = 0; i < n; i++) {
        for (size_t k = 0; k < n; k++) {
            double aik = a[i * n + k];
            for (size_t j = 0; j < n; j++) {
                c[i * n + j] += aik * b[k * n + j];  // kaikki riveittäin
            }
        }
    }
}
// @loppu ikj

// @alku lohkottu
enum { LOHKO = 64 };

static size_t pienempi(size_t x, size_t y)
{
    return x < y ? x : y;
}

// Kuten ikj, mutta k- ja j-silmukat kulkevat LOHKO x LOHKO -paloissa:
// b:n pala (32 KiB) ja c:n rivin pala pysyvät välimuistissa, kun
// samaa b:n palaa käytetään kaikilla i:n arvoilla.
[[gnu::noinline]] static void tulo_lohkottu(const double *a,
                                            const double *b,
                                            double *restrict c, size_t n)
{
    for (size_t i = 0; i < n * n; i++) {
        c[i] = 0;
    }
    for (size_t kk = 0; kk < n; kk += LOHKO) {
        size_t kl = pienempi(kk + LOHKO, n);
        for (size_t jj = 0; jj < n; jj += LOHKO) {
            size_t jl = pienempi(jj + LOHKO, n);
            for (size_t i = 0; i < n; i++) {
                for (size_t k = kk; k < kl; k++) {
                    double aik = a[i * n + k];
                    for (size_t j = jj; j < jl; j++) {
                        c[i * n + j] += aik * b[k * n + j];
                    }
                }
            }
        }
    }
}
// @loppu lohkottu

static double *luo(size_t n, uint64_t siemen)
{
    double *m = malloc(n * n * sizeof *m);
    if (m == NULL) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }
    // Pienet kokonaisluvut: tulot ja summat ovat tarkkoja, joten eri
    // järjestyksessä lasketut tulokset ovat bitilleen samat.
    Satunnainen r = {siemen};
    for (size_t i = 0; i < n * n; i++) {
        m[i] = (double)satunnainen_alle(&r, 10) - 5;
    }
    return m;
}

typedef void (*Tulo)(const double *, const double *, double *, size_t);

typedef struct {
    const double *a, *b;
    double *c;
    size_t n;
    Tulo tulo;
} Tila;

static void aja(void *p)
{
    Tila *t = p;
    t->tulo(t->a, t->b, t->c, t->n);
    kayta(t->c);
}

int main(int argc, char **argv)
{
    size_t n = 200;      // ei lohkon monikerta: reunat testataan
    if (argc == 3 && strcmp(argv[1], "--kerran") == 0) {
        n = strtoul(argv[2], NULL, 10);
    } else if (mittaustila(argc, argv)) {
        n = argc == 3 ? strtoul(argv[2], NULL, 10) : 512;
    }
    double *a = luo(n, 1), *b = luo(n, 2);
    double *c1 = malloc(n * n * sizeof *c1);
    double *c2 = malloc(n * n * sizeof *c2);
    double *c3 = malloc(n * n * sizeof *c3);
    if (c1 == NULL || c2 == NULL || c3 == NULL) {
        return EXIT_FAILURE;
    }
    if (mittaustila(argc, argv)) {
        printf("matriisitulo n = %zu (2n^3 = %.2g laskua)\n", n,
               2.0 * (double)n * (double)n * (double)n);
        Tila t[] = {{a, b, c1, n, tulo_ijk}, {a, b, c2, n, tulo_ikj},
                    {a, b, c3, n, tulo_lohkottu}};
        const char *nimet[] = {"ijk", "ikj", "lohkottu ikj"};
        double vertailu = 0;
        for (int i = 0; i < 3; i++) {
            Tilasto s = mittaa(aja, &t[i], 3);
            tulosta_mittaus(nimet[i], s, vertailu);
            printf("  %26s %10.2f GFLOP/s\n", "",
                   2.0 * (double)n * (double)n * (double)n
                       / (s.mediaani * 1e6));
            vertailu = i == 0 ? s.mediaani : vertailu;
        }
    } else {
        tulo_ijk(a, b, c1, n);
        tulo_ikj(a, b, c2, n);
        tulo_lohkottu(a, b, c3, n);
        double jalki = 0;
        for (size_t i = 0; i < n; i++) {
            jalki += c1[i * n + i];
        }
        bool samat = memcmp(c1, c2, n * n * sizeof *c1) == 0
                     && memcmp(c1, c3, n * n * sizeof *c1) == 0;
        printf("n = %zu, jalki %.0f, c[0][1] %.0f\n", n, jalki, c1[1]);
        printf("kaikki tulot samat: %s\n", samat ? "kylla" : "ei");
    }
    free(a);
    free(b);
    free(c1);
    free(c2);
    free(c3);
    return 0;
}
