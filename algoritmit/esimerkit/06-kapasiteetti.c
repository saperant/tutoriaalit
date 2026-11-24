// Haku vastauksen arvoalueelta: pienin kuorma-auton kapasiteetti, jolla
// paketit (annetussa järjestyksessä) ehditään ajaa D päivässä. Ehto
// "kapasiteetilla c ehtii" on monotoninen: jos c riittää, myös c + 1
// riittää. Silloin pienin riittävä c löytyy binäärihaulla.
#include <stdio.h>
#include <stdlib.h>

#include "satunnainen.h"

// @alku ehtii
// Ahne tarkistus O(n): lastataan pakettia niin kauan kuin mahtuu.
static bool ehtii(const int *paino, int n, int paivat, long kapasiteetti)
{
    int tarvitaan = 1;
    long kuorma = 0;
    for (int i = 0; i < n; i++) {
        if (paino[i] > kapasiteetti) {
            return false;
        }
        if (kuorma + paino[i] > kapasiteetti) {
            tarvitaan++;
            kuorma = 0;
        }
        kuorma += paino[i];
    }
    return tarvitaan <= paivat;
}
// @loppu ehtii

// @alku pienin
// Vastaus on välillä [suurin paketti, kaikkien summa]. Haetaan alarajaa
// kuten taulukosta: ensimmäinen c, jolla ehtii(c) on tosi.
static long pienin_kapasiteetti(const int *paino, int n, int paivat,
                                int *kokeiluja)
{
    long lo = 0, hi = 0;
    for (int i = 0; i < n; i++) {
        lo = paino[i] > lo ? paino[i] : lo;
        hi += paino[i];
    }
    *kokeiluja = 0;
    while (lo < hi) {
        long keski = lo + (hi - lo) / 2;
        ++*kokeiluja;
        if (ehtii(paino, n, paivat, keski)) {
            hi = keski;
        } else {
            lo = keski + 1;
        }
    }
    return lo;
}
// @loppu pienin

static long raaka(const int *paino, int n, int paivat)
{
    long c = 0;
    while (!ehtii(paino, n, paivat, c)) {
        c++;
    }
    return c;
}

int main(void)
{
    const int paino[] = { 4, 8, 15, 16, 23, 42, 7, 3, 12, 9 };
    const int n = sizeof paino / sizeof paino[0];
    for (int paivat = 1; paivat <= 5; paivat++) {
        int kokeiluja;
        long c = pienin_kapasiteetti(paino, n, paivat, &kokeiluja);
        printf("päiviä %d: kapasiteetti %3ld (%d kokeilua)\n",
               paivat, c, kokeiluja);
    }

    Satunnainen s = { 8 };
    int virheita = 0;
    for (int kierros = 0; kierros < 300; kierros++) {
        int m = 1 + (int)satunnainen_alle(&s, 20);
        int p[20];
        for (int i = 0; i < m; i++) {
            p[i] = 1 + (int)satunnainen_alle(&s, 30);
        }
        int paivat = 1 + (int)satunnainen_alle(&s, (uint32_t)m);
        int k;
        if (pienin_kapasiteetti(p, m, paivat, &k) != raaka(p, m, paivat)) {
            virheita++;
        }
    }
    printf("raakatesti: 300 tapausta, %d virhettä\n", virheita);
    return EXIT_SUCCESS;
}
