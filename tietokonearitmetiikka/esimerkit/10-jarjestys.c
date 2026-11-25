// Matriisin läpikäynti riveittäin ja sarakkeittain. Ilman argumentteja
// ohjelma tarkistaa vain tuloksen; argumentilla "mittaa" se vertaa
// aikoja (esimerkkien Makefile ajaa sen optimoituna).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static double sekunnit(void)
{
    struct timespec t;
    timespec_get(&t, TIME_UTC);        // C11:n vakiokirjastossa
    return (double)t.tv_sec + (double)t.tv_nsec * 1e-9;
}

// @alku indeksi
// Rivijärjestyksessä (C, NumPy) alkio (i, j) on kohdassa i*n + j.
static inline double alkio(const double *a, size_t n, size_t i, size_t j)
{
    return a[i * n + j];
}
// @loppu indeksi

int main(int argc, char **argv)
{
    bool mittaa = argc > 1 && strcmp(argv[1], "mittaa") == 0;
    size_t n = mittaa ? 4096 : 512;
    double *a = malloc(sizeof(double) * n * n);
    if (!a) {
        return 1;
    }
    for (size_t k = 0; k < n * n; k++) {
        a[k] = (double)(k % 7);
    }
    double paras_rivi = 1e9, paras_sarake = 1e9, s1 = 0, s2 = 0;
    for (int kierros = 0; kierros < 3; kierros++) {
        // @alku lapikaynti
        double t0 = sekunnit();
        s1 = 0.0;
        for (size_t i = 0; i < n; i++) {       // peräkkäiset osoitteet
            for (size_t j = 0; j < n; j++) {
                s1 += alkio(a, n, i, j);
            }
        }
        double t1 = sekunnit();
        s2 = 0.0;
        for (size_t j = 0; j < n; j++) {       // n * 8 tavun hypyt
            for (size_t i = 0; i < n; i++) {
                s2 += alkio(a, n, i, j);
            }
        }
        double t2 = sekunnit();
        // @loppu lapikaynti
        paras_rivi = t1 - t0 < paras_rivi ? t1 - t0 : paras_rivi;
        paras_sarake = t2 - t1 < paras_sarake ? t2 - t1 : paras_sarake;
    }
    printf("summat samat: %s\n", s1 == s2 ? "kyllä" : "ei");
    if (mittaa) {
        printf("riveittäin vähintään 3 kertaa nopeampi: %s\n",
               paras_sarake > 3.0 * paras_rivi ? "kyllä" : "ei");
    }
    free(a);
    return 0;
}
