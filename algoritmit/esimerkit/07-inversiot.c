// Inversioiden laskeminen hajota ja hallitse -menetelmällä. Inversio on
// pari i < j, jossa a[i] > a[j]. Raaka laskenta on O(n^2); lomituksen
// yhteydessä parit saadaan laskettua O(n log n) ajassa. Esimerkkinä
// kahden käyttäjän elokuvalistan erilaisuus (Kendallin etäisyys).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "satunnainen.h"

// @alku inversiot
// Lajittelee a[lo..hi) ja palauttaa inversioiden määrän. Kun oikean
// puolen alkio siirretään tulokseen ennen vasemman puolen alkioita,
// se muodostaa inversion jokaisen vasemmalle jääneen alkion kanssa.
static long inversiot(int *a, int *apu, int lo, int hi)
{
    if (hi - lo < 2) {
        return 0;
    }
    int keski = lo + (hi - lo) / 2;
    long maara = inversiot(a, apu, lo, keski) +
                 inversiot(a, apu, keski, hi);
    int i = lo, j = keski, k = lo;
    while (i < keski && j < hi) {
        if (a[i] <= a[j]) {
            apu[k++] = a[i++];
        } else {
            maara += keski - i;        // a[i..keski) > a[j]
            apu[k++] = a[j++];
        }
    }
    while (i < keski) {
        apu[k++] = a[i++];
    }
    while (j < hi) {
        apu[k++] = a[j++];
    }
    memcpy(a + lo, apu + lo, (size_t)(hi - lo) * sizeof *a);
    return maara;
}
// @loppu inversiot

static long raaka(const int *a, int n)
{
    long maara = 0;
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            maara += a[i] > a[j];
        }
    }
    return maara;
}

int main(void)
{
    // Käyttäjä B:n sijoitukset käyttäjä A:n järjestyksessä 1..8.
    int b[] = { 2, 1, 4, 3, 8, 5, 6, 7 };
    int apu[8];
    long r = raaka(b, 8);
    printf("elokuvalistat: %ld eriävää paria (raaka %ld)\n",
           inversiot(b, apu, 0, 8), r);

    Satunnainen s = { 13 };
    enum { N = 3000 };
    static int a[N], kopio[N], tila[N];
    int virheita = 0;
    for (int kierros = 0; kierros < 20; kierros++) {
        int n = 1 + (int)satunnainen_alle(&s, N);
        for (int i = 0; i < n; i++) {
            a[i] = kopio[i] = (int)satunnainen_alle(&s, 1000);
        }
        if (inversiot(a, tila, 0, n) != raaka(kopio, n)) {
            virheita++;
        }
    }
    printf("raakatesti: 20 taulukkoa, %d virhettä\n", virheita);
    return EXIT_SUCCESS;
}
