// Lähimmän pisteen haku: kutsu toiseen käännösyksikköön kuumassa
// silmukassa. Ilman LTO:ta kääntäjä ei näe etaisyys2-funktion sisään.
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>

#include "../mittari.h"
#include "../satunnainen.h"
#include "geometria.h"

// @alku lahin
// Indeksi pisteeseen, joka on lähinnä pistettä p.
static size_t lahin(const Piste *pisteet, size_t n, Piste p)
{
    size_t paras = 0;
    double paras_d = etaisyys2(pisteet[0], p);
    for (size_t i = 1; i < n; i++) {
        double d = etaisyys2(pisteet[i], p);   // kutsu joka kierroksella
        if (d < paras_d) {
            paras_d = d;
            paras = i;
        }
    }
    return paras;
}
// @loppu lahin

static Piste *luo(size_t n, uint64_t siemen)
{
    Piste *p = malloc(n * sizeof *p);
    if (p == NULL) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }
    Satunnainen r = {siemen};
    for (size_t i = 0; i < n; i++) {
        p[i] = (Piste){satunnainen_alle(&r, 100000) / 10.0,
                       satunnainen_alle(&r, 100000) / 10.0};
    }
    return p;
}

typedef struct {
    const Piste *pisteet, *haut;
    size_t n, hakuja, summa;
} Tila;

static void aja(void *p)
{
    Tila *t = p;
    size_t s = 0;
    for (size_t i = 0; i < t->hakuja; i++) {
        s += lahin(t->pisteet, t->n, t->haut[i]);
    }
    t->summa = s;
    kayta(&t->summa);
}

int main(int argc, char **argv)
{
    bool mittaus = mittaustila(argc, argv);
    size_t n = mittaus ? 4000 : 500, hakuja = mittaus ? 4000 : 100;
    Piste *pisteet = luo(n, 1), *haut = luo(hakuja, 2);
    Tila t = {pisteet, haut, n, hakuja, 0};
    if (mittaus) {
        Tilasto s = mittaa(aja, &t, 11);
        printf("lahin piste: %zu hakua %zu pisteesta: %.2f ms\n", hakuja,
               n, s.mediaani);
    } else {
        aja(&t);
        size_t i = lahin(pisteet, n, haut[0]);
        printf("lahin pisteelle (%.1f, %.1f): %zu (%.1f, %.1f)\n",
               haut[0].x, haut[0].y, i, pisteet[i].x, pisteet[i].y);
        printf("indeksien summa %zu\n", t.summa);
    }
    free(pisteet);
    free(haut);
    return 0;
}
