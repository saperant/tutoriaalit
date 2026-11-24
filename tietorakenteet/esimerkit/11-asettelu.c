// Välimuistirivit: suoritin hakee muistia 64 tavun riveinä. Lasketaan,
// montaa eri riviä läpikäynti koskettaa, kun sama data on taulukossa,
// linkitetyssä listassa ja kahdessa tietueasettelussa.
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "satunnainen.h"

enum { N = 1 << 16, RIVI = 64 };

// @alku laskuri
// Laskee rivinvaihdot: kuinka monta kertaa peräkkäiset osoitteet
// osuvat eri 64 tavun riviin. Tämä on alaraja välimuistihuteille.
typedef struct {
    uintptr_t edellinen;
    long vaihtoja;
} Rivilaskuri;

static void kosketa(Rivilaskuri *r, const void *osoite)
{
    uintptr_t rivi = (uintptr_t)osoite / RIVI;
    if (rivi != r->edellinen) {
        r->vaihtoja++;
        r->edellinen = rivi;
    }
}
// @loppu laskuri

typedef struct solmu {
    int arvo;
    struct solmu *seuraava;
} Solmu;

// @alku tietue
typedef struct {            // 32 tavua: kaksi hiukkasta riviin
    float x, y, z;
    float vx, vy, vz;
    uint32_t tyyppi, tila;
} Hiukkanen;

typedef struct {            // sama data kenttä kerrallaan
    float *x, *y, *z, *vx, *vy, *vz;
} Hiukkaset;
// @loppu tietue

int main(void)
{
    // @alku taulukko
    int *taulukko = aligned_alloc(RIVI, N * sizeof *taulukko);
    Solmu *solmut = aligned_alloc(RIVI, N * sizeof *solmut);
    uint32_t *jarjestys = malloc(N * sizeof *jarjestys);
    if (taulukko == nullptr || solmut == nullptr || jarjestys == nullptr) {
        return EXIT_FAILURE;
    }
    // Lista rakennetaan satunnaisessa järjestyksessä, kuten käy, kun
    // solmuja lisätään ja poistetaan pitkään: muistissa vierekkäiset
    // solmut eivät ole listassa peräkkäin.
    Satunnainen s = {1};
    for (uint32_t i = 0; i < N; i++) {
        jarjestys[i] = i;
    }
    for (uint32_t i = N - 1; i > 0; i--) {
        uint32_t j = satunnainen_alle(&s, i + 1);
        uint32_t apu = jarjestys[i];
        jarjestys[i] = jarjestys[j];
        jarjestys[j] = apu;
    }
    for (uint32_t i = 0; i < N; i++) {
        taulukko[i] = (int)i;
        solmut[jarjestys[i]].arvo = (int)i;
        solmut[jarjestys[i]].seuraava =
            i + 1 < N ? &solmut[jarjestys[i + 1]] : nullptr;
    }

    Rivilaskuri t = {0, 0}, l = {0, 0};
    long summa_t = 0, summa_l = 0;
    for (uint32_t i = 0; i < N; i++) {
        kosketa(&t, &taulukko[i]);
        summa_t += taulukko[i];
    }
    for (const Solmu *p = &solmut[jarjestys[0]]; p != nullptr;
         p = p->seuraava) {
        kosketa(&l, p);
        summa_l += p->arvo;
    }
    printf("%d kokonaislukua, summat samat: %s\n", N,
           summa_t == summa_l ? "kyllä" : "EI");
    printf("taulukko:  %6ld rivinvaihtoa\n", t.vaihtoja);
    printf("lista:     %6ld rivinvaihtoa\n", l.vaihtoja);
    // @loppu taulukko

    // @alku asettelu
    // Lasketaan vain x-koordinaattien summa: tietuetaulukko (AoS) tuo
    // välimuistiin kaikki kentät, kenttätaulukot (SoA) vain tarvitun.
    Hiukkanen *aos = aligned_alloc(RIVI, N * sizeof *aos);
    float *x = aligned_alloc(RIVI, N * sizeof *x);
    if (aos == nullptr || x == nullptr) {
        return EXIT_FAILURE;
    }
    Hiukkaset soa = {.x = x};
    for (uint32_t i = 0; i < N; i++) {
        aos[i] = (Hiukkanen){.x = (float)i};
        soa.x[i] = (float)i;
    }
    Rivilaskuri ra = {0, 0}, rs = {0, 0};
    double sa = 0, ss = 0;
    for (uint32_t i = 0; i < N; i++) {
        kosketa(&ra, &aos[i].x);
        sa += aos[i].x;
        kosketa(&rs, &soa.x[i]);
        ss += soa.x[i];
    }
    printf("x-summa, tietuetaulukko (AoS): %6ld rivinvaihtoa\n",
           ra.vaihtoja);
    printf("x-summa, kenttätaulukot (SoA): %6ld rivinvaihtoa\n",
           rs.vaihtoja);
    // @loppu asettelu

    free(taulukko);
    free(solmut);
    free(jarjestys);
    free(aos);
    free(x);
    return summa_t == summa_l && sa == ss ? EXIT_SUCCESS : EXIT_FAILURE;
}
