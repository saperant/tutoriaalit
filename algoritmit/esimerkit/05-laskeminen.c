// Lajittelu ilman vertailuja: laskemislajittelu pienelle avainalueelle
// (koepisteet 0-60) ja kantalukulajittelu 32-bittisille avaimille.
// Kumpikin on vakaa ja lineaarinen; tulos tarkistetaan qsortilla.
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "satunnainen.h"

// @alku laskeminen
// Laskemislajittelu: lasketaan kunkin avaimen esiintymät, muutetaan
// ne alkukohdiksi (etuliitesummat) ja sijoitetaan alkiot järjestyksessä.
// Aika O(n + k), missä k on avainalueen koko. Vakaa.
enum { PISTEET = 61 };

typedef struct {
    int pisteet;
    int opiskelija;
} Tulos;

static void laskemislajittelu(const Tulos *a, Tulos *ulos, int n)
{
    int alku[PISTEET + 1] = { 0 };
    for (int i = 0; i < n; i++) {
        alku[a[i].pisteet + 1]++;
    }
    for (int k = 0; k < PISTEET; k++) {
        alku[k + 1] += alku[k];        // alku[k] = pienempien määrä
    }
    for (int i = 0; i < n; i++) {
        ulos[alku[a[i].pisteet]++] = a[i];
    }
}
// @loppu laskeminen

// @alku kantaluku
// Kantalukulajittelu (LSD): neljä laskemislajittelukierrosta tavu
// kerrallaan vähiten merkitsevästä alkaen. Koska jokainen kierros on
// vakaa, aiempien tavujen järjestys säilyy. Aika O(4 (n + 256)).
static void kantaluku(uint32_t *a, uint32_t *apu, int n)
{
    for (int siirto = 0; siirto < 32; siirto += 8) {
        int alku[257] = { 0 };
        for (int i = 0; i < n; i++) {
            alku[((a[i] >> siirto) & 0xFF) + 1]++;
        }
        for (int k = 0; k < 256; k++) {
            alku[k + 1] += alku[k];
        }
        for (int i = 0; i < n; i++) {
            apu[alku[(a[i] >> siirto) & 0xFF]++] = a[i];
        }
        memcpy(a, apu, (size_t)n * sizeof *a);
    }
}
// @loppu kantaluku

static int vertaa(const void *x, const void *y)
{
    uint32_t a = *(const uint32_t *)x, b = *(const uint32_t *)y;
    return (a > b) - (a < b);
}

int main(void)
{
    Satunnainen s = { 11 };

    const Tulos kurssi[] = {
        { 42, 1 }, { 17, 2 }, { 42, 3 }, { 60, 4 },
        { 0, 5 },  { 17, 6 }, { 35, 7 }, { 42, 8 },
    };
    enum { K = sizeof kurssi / sizeof kurssi[0] };
    Tulos jarj[K];
    laskemislajittelu(kurssi, jarj, K);
    printf("pisteet (opiskelija):");
    for (int i = 0; i < K; i++) {
        printf(" %d(%d)", jarj[i].pisteet, jarj[i].opiskelija);
    }
    printf("\n");

    enum { N = 100000 };
    static uint32_t a[N], apu[N], b[N];
    for (int i = 0; i < N; i++) {
        a[i] = b[i] = (uint32_t)satunnainen_seuraava(&s);
    }
    kantaluku(a, apu, N);
    qsort(b, N, sizeof *b, vertaa);
    printf("kantaluku: %d avainta, sama kuin qsort: %s\n", N,
           memcmp(a, b, sizeof a) == 0 ? "kyllä" : "ei");
    return EXIT_SUCCESS;
}
