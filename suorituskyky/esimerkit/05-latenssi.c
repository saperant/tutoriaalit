// Muistiviive työjoukon koon funktiona: osoitinjahti.
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>

#include "mittari.h"
#include "satunnainen.h"

// @alku solmu
// Yksi solmu täyttää yhden välimuistirivin, joten jokainen lataus
// koskee eri riviä eikä viereisten rivien esihaku auta.
typedef struct Solmu {
    struct Solmu *seuraava;
    char tayte[64 - sizeof(struct Solmu *)];
} Solmu;
// @loppu solmu

// @alku sattolo
// Sattolon algoritmi: satunnainen permutaatio, joka on yksi ainoa
// sykli. Jahti käy siis kaikki solmut läpi ennen kuin palaa alkuun.
static void kytke_sykliksi(Solmu *s, size_t n, Satunnainen *r)
{
    size_t *jarjestys = malloc(n * sizeof *jarjestys);
    if (jarjestys == NULL) {
        exit(EXIT_FAILURE);
    }
    for (size_t i = 0; i < n; i++) {
        jarjestys[i] = i;
    }
    for (size_t i = n - 1; i > 0; i--) {
        size_t j = satunnainen_seuraava(r) % i;     // j < i
        size_t t = jarjestys[i];
        jarjestys[i] = jarjestys[j];
        jarjestys[j] = t;
    }
    for (size_t i = 0; i < n; i++) {
        s[i].seuraava = &s[jarjestys[i]];
    }
    free(jarjestys);
}
// @loppu sattolo

// @alku jahti
// Jokainen lataus riippuu edellisestä: suoritin ei voi aloittaa
// seuraavaa ennen kuin edellinen on valmis. Aika per askel = viive.
[[gnu::noinline]] static Solmu *jahtaa(Solmu *p, size_t askelia)
{
    while (askelia-- > 0) {
        p = p->seuraava;
    }
    return p;
}
// @loppu jahti

typedef struct {
    Solmu *alku;
    size_t askelia;
} Tila;

static void aja(void *p)
{
    Tila *t = p;
    t->alku = jahtaa(t->alku, t->askelia);
    kayta(t->alku);
}

int main(int argc, char **argv)
{
    Satunnainen r = {42};
    if (mittaustila(argc, argv)) {
        printf("osoitinjahti, satunnainen sykli\n");
        printf("  tyojoukko   ns/lataus\n");
        for (size_t koko = 16 << 10; koko <= (size_t)256 << 20; koko *= 4) {
            size_t n = koko / sizeof(Solmu);
            Solmu *s = aligned_alloc(64, n * sizeof *s);
            if (s == NULL) {
                return EXIT_FAILURE;
            }
            kytke_sykliksi(s, n, &r);
            Tila t = {s, 1 << 20};
            Tilasto ti = mittaa(aja, &t, 3);
            printf("  %6zu KiB  %9.2f\n", koko >> 10,
                   ti.mediaani * 1e6 / (double)t.askelia);
            free(s);
        }
        return 0;
    }
    // Toiminnallinen testi: sykli kattaa kaikki solmut.
    enum { N = 1000 };
    Solmu *s = aligned_alloc(64, N * sizeof *s);
    if (s == NULL) {
        return EXIT_FAILURE;
    }
    kytke_sykliksi(s, N, &r);
    size_t pituus = 1;
    for (Solmu *p = s->seuraava; p != s; p = p->seuraava) {
        pituus++;
    }
    printf("solmun koko %zu tavua\n", sizeof(Solmu));
    printf("syklin pituus %zu / %d\n", pituus, N);
    printf("jahti palaa alkuun %d askeleessa: %s\n", N,
           jahtaa(s, N) == s ? "kylla" : "ei");
    free(s);
    return 0;
}
