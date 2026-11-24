// Lomituslajittelu ja vakaus: tilaukset ovat aikajärjestyksessä, ja ne
// lajitellaan asiakkaan mukaan. Vakaa lajittelu säilyttää kunkin
// asiakkaan tilausten aikajärjestyksen; epävakaa ei.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "satunnainen.h"

typedef struct {
    char asiakas;      // lajitteluavain
    int kello;         // alkuperäinen järjestys
} Tilaus;

// @alku lomitus
// Lomitus: kaksi järjestettyä puoliskoa yhdistetään apuun ja kopioidaan
// takaisin. Tasapelissä otetaan vasen alkio, joten lajittelu on vakaa.
// Aika O(n log n) aina, lisämuisti O(n).
static void lomita(Tilaus *a, Tilaus *apu, int n)
{
    if (n < 2) {
        return;
    }
    int m = n / 2;
    lomita(a, apu, m);
    lomita(a + m, apu, n - m);
    int i = 0, j = m, k = 0;
    while (i < m && j < n) {
        if (a[j].asiakas < a[i].asiakas) {   // ei <=: vasen voittaa
            apu[k++] = a[j++];
        } else {
            apu[k++] = a[i++];
        }
    }
    while (i < m) {
        apu[k++] = a[i++];
    }
    while (j < n) {
        apu[k++] = a[j++];
    }
    memcpy(a, apu, (size_t)n * sizeof *a);
}
// @loppu lomitus

// Valintalajittelu vaihtaa pienimmän alkion paikalleen; vaihto voi
// hypätä yhtä suurten yli, joten se ei ole vakaa.
static void valinta(Tilaus *a, int n)
{
    for (int i = 0; i < n - 1; i++) {
        int p = i;
        for (int j = i + 1; j < n; j++) {
            if (a[j].asiakas < a[p].asiakas) {
                p = j;
            }
        }
        Tilaus t = a[i];
        a[i] = a[p];
        a[p] = t;
    }
}

static void tulosta(const char *nimi, const Tilaus *a, int n)
{
    printf("%-9s", nimi);
    for (int i = 0; i < n; i++) {
        printf(" %c%d", a[i].asiakas, a[i].kello);
    }
    printf("\n");
}

// @alku vakaus
// Vakaus tarkistetaan: saman avaimen alkioiden on oltava alkuperäisessä
// järjestyksessä.
static bool vakaa(const Tilaus *a, int n)
{
    for (int i = 1; i < n; i++) {
        if (a[i - 1].asiakas > a[i].asiakas ||
            (a[i - 1].asiakas == a[i].asiakas &&
             a[i - 1].kello > a[i].kello)) {
            return false;
        }
    }
    return true;
}
// @loppu vakaus

int main(void)
{
    const Tilaus alku[] = {
        { 'C', 1 }, { 'A', 2 }, { 'B', 3 }, { 'A', 4 },
        { 'C', 5 }, { 'B', 6 }, { 'A', 7 }, { 'C', 8 },
    };
    enum { N = sizeof alku / sizeof alku[0] };
    Tilaus a[N], apu[N];

    tulosta("alku:", alku, N);
    memcpy(a, alku, sizeof a);
    lomita(a, apu, N);
    tulosta("lomitus:", a, N);
    memcpy(a, alku, sizeof a);
    valinta(a, N);
    tulosta("valinta:", a, N);

    // Satunnaistettu testi: 500 taulukkoa, pieni avainalue tuottaa
    // paljon yhtä suuria avaimia.
    Satunnainen s = { 42 };
    int virheita = 0;
    for (int t = 0; t < 500; t++) {
        enum { M = 64 };
        Tilaus b[M], tmp[M];
        int n = (int)satunnainen_alle(&s, M + 1);
        for (int i = 0; i < n; i++) {
            b[i] = (Tilaus){ (char)('A' + satunnainen_alle(&s, 4)), i };
        }
        lomita(b, tmp, n);
        virheita += !vakaa(b, n);
    }
    printf("satunnaistesti: 500 taulukkoa, %d virhettä\n", virheita);
    return EXIT_SUCCESS;
}
