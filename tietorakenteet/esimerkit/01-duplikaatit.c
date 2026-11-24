// Kuinka moni kirjautumislokin käyttäjätunnus esiintyy useammin kuin
// kerran? Sama kysymys kolmella tietorakenteella; operaatioiden määrä
// kertoo, miksi rakenteen valinnalla on väliä.
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "satunnainen.h"

enum { N = 5000, MAKSIMI = 20000 };

static long vertailuja;

// @alku naiivi
// Jokainen alkio verrataan kaikkiin aiempiin: noin n^2 / 2 vertailua.
static int naiivi(const int *tunnus, int n)
{
    int toistuvia = 0;
    for (int i = 0; i < n; i++) {
        int aiempia = 0;
        for (int j = 0; j < i; j++) {
            vertailuja++;
            if (tunnus[j] == tunnus[i]) {
                aiempia++;
            }
        }
        toistuvia += aiempia == 1;   // lasketaan toisella esiintymällä
    }
    return toistuvia;
}
// @loppu naiivi

// Lomituslajittelu, joka laskee vertailut. Standardin qsort kävisi
// myös, mutta sen vertailujen määrä riippuu C-kirjaston toteutuksesta.
static void lajittele(int *a, int *apu, int n)
{
    if (n < 2) {
        return;
    }
    int m = n / 2;
    lajittele(a, apu, m);
    lajittele(a + m, apu, n - m);
    int i = 0, j = m, k = 0;
    while (i < m && j < n) {
        vertailuja++;
        apu[k++] = a[j] < a[i] ? a[j++] : a[i++];
    }
    while (i < m) {
        apu[k++] = a[i++];
    }
    while (j < n) {
        apu[k++] = a[j++];
    }
    memcpy(a, apu, (size_t)n * sizeof *a);
}

// @alku lajittelu
// Lajittelun jälkeen samat tunnukset ovat vierekkäin: n log n
// vertailua lajitteluun ja yksi läpikäynti.
static int lajittelemalla(const int *tunnus, int n)
{
    int *kopio = malloc(2 * (size_t)n * sizeof *kopio);
    if (kopio == nullptr) {
        return -1;
    }
    memcpy(kopio, tunnus, (size_t)n * sizeof *kopio);
    lajittele(kopio, kopio + n, n);     // jälkimmäinen puolisko apuna
    int toistuvia = 0;
    for (int i = 1; i < n; i++) {
        bool uusi_toisto = kopio[i] == kopio[i - 1]
                           && (i < 2 || kopio[i - 2] != kopio[i]);
        toistuvia += uusi_toisto;
    }
    free(kopio);
    return toistuvia;
}
// @loppu lajittelu

// @alku taulukko
// Tunnukset ovat pieniä kokonaislukuja, joten ne käyvät suoraan
// indekseiksi: yksi läpikäynti, ei vertailuja, mutta muistia kuluu
// koko arvoalueen verran.
static int laskurilla(const int *tunnus, int n)
{
    unsigned char *nahty = calloc(MAKSIMI, 1);
    if (nahty == nullptr) {
        return -1;
    }
    int toistuvia = 0;
    for (int i = 0; i < n; i++) {
        if (nahty[tunnus[i]] == 1) {
            toistuvia++;
        }
        if (nahty[tunnus[i]] < 2) {
            nahty[tunnus[i]]++;
        }
    }
    free(nahty);
    return toistuvia;
}
// @loppu taulukko

int main(void)
{
    static int tunnus[N];
    Satunnainen s = {2026};
    for (int i = 0; i < N; i++) {
        tunnus[i] = (int)satunnainen_alle(&s, MAKSIMI);
    }

    vertailuja = 0;
    int a = naiivi(tunnus, N);
    printf("naiivi:      %d toistuvaa, %ld vertailua\n", a, vertailuja);
    vertailuja = 0;
    int b = lajittelemalla(tunnus, N);
    printf("lajittelu:   %d toistuvaa, %ld vertailua\n", b, vertailuja);
    int c = laskurilla(tunnus, N);
    printf("laskuri:     %d toistuvaa, %d taulukon lukua\n", c, N);
    return a == b && b == c ? EXIT_SUCCESS : EXIT_FAILURE;
}
