// Rakenteiden taulukko (AoS) ja taulukoiden rakenne (SoA).
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>

#include "mittari.h"
#include "satunnainen.h"

// @alku aos
// AoS: yksi rakenne hiukkasta kohden, 80 tavua.
typedef struct {
    double x, y, z;
    double vx, vy, vz;
    double massa, varaus;
    int tunnus, laji;
    double ika;
} Hiukkanen;

[[gnu::noinline]] static void siirra_aos(Hiukkanen *h, size_t n,
                                         double dt)
{
    for (size_t i = 0; i < n; i++) {
        h[i].x += h[i].vx * dt;     // käyttää 16 tavua 80:stä
    }
}
// @loppu aos

// @alku soa
// SoA: kukin kenttä omassa taulukossaan.
typedef struct {
    double *x, *y, *z;
    double *vx, *vy, *vz;
    double *massa, *varaus;
    int *tunnus, *laji;
    double *ika;
} Hiukkaset;

[[gnu::noinline]] static void siirra_soa(Hiukkaset *h, size_t n,
                                         double dt)
{
    double *restrict x = h->x;
    const double *restrict vx = h->vx;
    for (size_t i = 0; i < n; i++) {
        x[i] += vx[i] * dt;         // käyttää kaikki ladatut tavut
    }
}
// @loppu soa

static void *varaa(size_t n, size_t koko)
{
    void *p = calloc(n, koko);
    if (p == NULL) {
        perror("calloc");
        exit(EXIT_FAILURE);
    }
    return p;
}

static void luo(size_t n, Hiukkanen **aos, Hiukkaset *soa)
{
    *aos = varaa(n, sizeof **aos);
    double **kentat[] = {&soa->x, &soa->y, &soa->z, &soa->vx, &soa->vy,
                         &soa->vz, &soa->massa, &soa->varaus, &soa->ika};
    for (size_t k = 0; k < sizeof kentat / sizeof kentat[0]; k++) {
        *kentat[k] = varaa(n, sizeof(double));
    }
    soa->tunnus = varaa(n, sizeof(int));
    soa->laji = varaa(n, sizeof(int));
    Satunnainen r = {7};
    for (size_t i = 0; i < n; i++) {
        double x = satunnainen_alle(&r, 1000);
        double vx = (double)satunnainen_alle(&r, 64) - 32;
        (*aos)[i] = (Hiukkanen){.x = x, .vx = vx, .massa = 1,
                                .tunnus = (int)i};
        soa->x[i] = x;
        soa->vx[i] = vx;
        soa->massa[i] = 1;
        soa->tunnus[i] = (int)i;
    }
}

static void vapauta(Hiukkanen *aos, Hiukkaset *soa)
{
    free(aos);
    double *kentat[] = {soa->x, soa->y, soa->z, soa->vx, soa->vy,
                        soa->vz, soa->massa, soa->varaus, soa->ika};
    for (size_t k = 0; k < sizeof kentat / sizeof kentat[0]; k++) {
        free(kentat[k]);
    }
    free(soa->tunnus);
    free(soa->laji);
}

typedef struct {
    Hiukkanen *aos;
    Hiukkaset *soa;
    size_t n;
} Tila;

static void aja_aos(void *p)
{
    Tila *t = p;
    siirra_aos(t->aos, t->n, 0.25);
    kayta(t->aos);
}

static void aja_soa(void *p)
{
    Tila *t = p;
    siirra_soa(t->soa, t->n, 0.25);
    kayta(t->soa->x);
}

int main(int argc, char **argv)
{
    size_t n = mittaustila(argc, argv) ? 4u << 20 : 10000;
    if (argc == 3 && strcmp(argv[1], "--kerran") == 0) {
        n = strtoul(argv[2], NULL, 10);
    }
    Hiukkanen *aos;
    Hiukkaset soa;
    luo(n, &aos, &soa);
    if (mittaustila(argc, argv)) {
        Tila t = {aos, &soa, n};
        printf("x += vx * dt, %zu hiukkasta (AoS %zu MiB)\n", n,
               n * sizeof *aos >> 20);
        Tilasto ta = mittaa(aja_aos, &t, 21);
        Tilasto ts = mittaa(aja_soa, &t, 21);
        tulosta_mittaus("AoS", ta, 0);
        tulosta_mittaus("SoA", ts, ta.mediaani);
    } else {
        // @alku testi
        for (int k = 0; k < 8; k++) {
            siirra_aos(aos, n, 0.25);
            siirra_soa(&soa, n, 0.25);
        }
        bool samat = true;
        double summa = 0;
        for (size_t i = 0; i < n; i++) {
            samat = samat && aos[i].x == soa.x[i];
            summa += soa.x[i];
        }
        printf("sizeof(Hiukkanen) = %zu\n", sizeof(Hiukkanen));
        printf("paikat samat: %s, summa %.2f\n", samat ? "kylla" : "ei",
               summa);
        // @loppu testi
    }
    vapauta(aos, &soa);
    return 0;
}
