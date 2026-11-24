// 0/1-reppuongelma dynaamisella ohjelmoinnilla: valitaan tavarat, joiden
// yhteispaino on enintään W ja arvo suurin. Taulukko paras[i][w] on
// suurin arvo, joka saadaan i ensimmäisellä tavaralla painorajalla w.
// Ratkaisu rekonstruoidaan taulukosta, ja tulos tarkistetaan raa'alla
// haulla satunnaisilla syötteillä.
#include <stdio.h>
#include <stdlib.h>

#include "satunnainen.h"

enum { MAX_N = 16, MAX_W = 100 };

typedef struct {
    const char *nimi;
    int paino, arvo;
} Tavara;

// @alku reppu
// paras[i][w] = max(paras[i-1][w],                      tavara i pois
//                   paras[i-1][w - p_i] + a_i)          tavara i mukaan
// Aika ja muisti O(n W). Palauttaa arvon ja merkitsee valitut tavarat.
static int reppu(const Tavara *t, int n, int raja, bool *valittu)
{
    static int paras[MAX_N + 1][MAX_W + 1];
    for (int w = 0; w <= raja; w++) {
        paras[0][w] = 0;
    }
    for (int i = 1; i <= n; i++) {
        for (int w = 0; w <= raja; w++) {
            paras[i][w] = paras[i - 1][w];
            int p = t[i - 1].paino;
            if (p <= w && paras[i - 1][w - p] + t[i - 1].arvo > paras[i][w]) {
                paras[i][w] = paras[i - 1][w - p] + t[i - 1].arvo;
            }
        }
    }
    // Rekonstruktio: jos arvo muuttui rivillä i, tavara i on mukana.
    int w = raja;
    for (int i = n; i >= 1; i--) {
        valittu[i - 1] = paras[i][w] != paras[i - 1][w];
        if (valittu[i - 1]) {
            w -= t[i - 1].paino;
        }
    }
    return paras[n][raja];
}
// @loppu reppu

static int raaka(const Tavara *t, int n, int raja)
{
    int paras = 0;
    for (unsigned joukko = 0; joukko < (1u << n); joukko++) {
        int paino = 0, arvo = 0;
        for (int i = 0; i < n; i++) {
            if (joukko >> i & 1) {
                paino += t[i].paino;
                arvo += t[i].arvo;
            }
        }
        if (paino <= raja && arvo > paras) {
            paras = arvo;
        }
    }
    return paras;
}

int main(void)
{
    // Retkireppu: painot sadoissa grammoissa, arvo on hyöty pisteinä.
    const Tavara retki[] = {
        { "teltta", 25, 40 },   { "makuupussi", 15, 30 },
        { "retkikeitin", 8, 15 }, { "kamera", 6, 9 },
        { "kirja", 4, 4 },      { "sadetakki", 5, 12 },
        { "ruoka", 20, 35 },    { "vesipullo", 10, 20 },
    };
    const int n = sizeof retki / sizeof retki[0];
    bool valittu[MAX_N];
    int arvo = reppu(retki, n, 60, valittu);
    int paino = 0;
    for (int i = 0; i < n; i++) {
        paino += valittu[i] ? retki[i].paino : 0;
    }
    printf("raja 6,0 kg: arvo %d, paino %d,%d kg\nmukaan:", arvo,
           paino / 10, paino % 10);
    for (int i = 0; i < n; i++) {
        if (valittu[i]) {
            printf(" %s", retki[i].nimi);
        }
    }
    printf("\n");

    Satunnainen s = { 23 };
    int virheita = 0;
    for (int k = 0; k < 300; k++) {
        int m = 1 + (int)satunnainen_alle(&s, MAX_N);
        Tavara t[MAX_N];
        for (int i = 0; i < m; i++) {
            t[i] = (Tavara){ "", 1 + (int)satunnainen_alle(&s, 30),
                             (int)satunnainen_alle(&s, 50) };
        }
        int r = (int)satunnainen_alle(&s, MAX_W + 1);
        int a = reppu(t, m, r, valittu);
        int p = 0, summa = 0;
        for (int i = 0; i < m; i++) {
            if (valittu[i]) {
                p += t[i].paino;
                summa += t[i].arvo;
            }
        }
        // Arvon on oltava optimi, ja valittujen on toteutettava se.
        if (a != raaka(t, m, r) || summa != a || p > r) {
            virheita++;
        }
    }
    printf("raakatesti: 300 tapausta, %d virhettä\n", virheita);
    return EXIT_SUCCESS;
}
