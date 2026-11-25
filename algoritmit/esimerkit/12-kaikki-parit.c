// Kaikkien parien lyhimmät polut Floydin–Warshallin algoritmilla:
// dynaaminen ohjelmointi välisolmujen joukon yli. Tulos tarkistetaan
// ajamalla Bellman–Ford jokaisesta lähtösolmusta.
#include <stdio.h>
#include <stdlib.h>

#include "satunnainen.h"

enum { MAX_N = 12, EI_REITTIA = 1 << 29 };

// @alku floyd
// Kierroksen k jälkeen d[u][v] on lyhin polku, jonka välisolmut
// kuuluvat joukkoon {0, ..., k}. Polku joko ei käytä solmua k tai
// kulkee sen kautta: d[u][v] = min(d[u][v], d[u][k] + d[k][v]).
// Palauttaa false, jos graafissa on negatiivinen sykli.
static bool floyd_warshall(int n, int d[MAX_N][MAX_N])
{
    for (int k = 0; k < n; k++) {
        for (int u = 0; u < n; u++) {
            for (int v = 0; v < n; v++) {
                if (d[u][k] < EI_REITTIA && d[k][v] < EI_REITTIA &&
                    d[u][k] + d[k][v] < d[u][v]) {
                    d[u][v] = d[u][k] + d[k][v];
                }
            }
        }
    }
    for (int u = 0; u < n; u++) {
        if (d[u][u] < 0) {
            return false;       // solmusta pääsee itseensä alle nollalla
        }
    }
    return true;
}
// @loppu floyd

// Vertailu: Bellman–Ford lähtösolmusta s kaarimatriisilla.
static bool bellman_ford(int n, int paino[MAX_N][MAX_N], int s, int *e)
{
    for (int v = 0; v < n; v++) {
        e[v] = v == s ? 0 : EI_REITTIA;
    }
    for (int kierros = 0; kierros < n; kierros++) {
        bool muuttui = false;
        for (int u = 0; u < n; u++) {
            for (int v = 0; v < n; v++) {
                if (u != v && e[u] < EI_REITTIA &&
                    paino[u][v] < EI_REITTIA &&
                    e[u] + paino[u][v] < e[v]) {
                    e[v] = e[u] + paino[u][v];
                    muuttui = true;
                }
            }
        }
        if (!muuttui) {
            return true;
        }
    }
    return false;               // n:s kierros paransi: negatiivinen sykli
}

int main(void)
{
    // @alku tiet
    // Tieverkon osa: etäisyydet kilometreinä, tiet kaksisuuntaisia.
    static const char *const kaupunki[] = {
        "Helsinki", "Lahti", "Tampere", "Mikkeli", "Kuopio",
    };
    static const int tiet[][3] = {
        { 0, 1, 105 }, { 0, 2, 180 }, { 1, 2, 130 }, { 1, 3, 135 },
        { 3, 4, 165 }, { 2, 4, 295 },
    };
    enum { N = 5 };
    static int d[MAX_N][MAX_N];
    for (int u = 0; u < N; u++) {
        for (int v = 0; v < N; v++) {
            d[u][v] = u == v ? 0 : EI_REITTIA;
        }
    }
    for (size_t i = 0; i < sizeof tiet / sizeof tiet[0]; i++) {
        d[tiet[i][0]][tiet[i][1]] = d[tiet[i][1]][tiet[i][0]] = tiet[i][2];
    }
    floyd_warshall(N, d);
    // @loppu tiet
    printf("%-10s", "");
    for (int v = 0; v < N; v++) {
        printf(" %9s", kaupunki[v]);
    }
    printf("\n");
    for (int u = 0; u < N; u++) {
        printf("%-10s", kaupunki[u]);
        for (int v = 0; v < N; v++) {
            printf(" %9d", d[u][v]);
        }
        printf("\n");
    }

    // Satunnaiset suunnatut graafit, joissa on myös negatiivisia kaaria.
    Satunnainen s = { 67 };
    int virheita = 0, syklisia = 0;
    for (int kierros = 0; kierros < 300; kierros++) {
        int n = 1 + (int)satunnainen_alle(&s, MAX_N);
        static int paino[MAX_N][MAX_N], fw[MAX_N][MAX_N];
        for (int u = 0; u < n; u++) {
            for (int v = 0; v < n; v++) {
                paino[u][v] = u == v ? 0
                    : satunnainen_alle(&s, 3) == 0
                        ? (int)satunnainen_alle(&s, 40) - 4 : EI_REITTIA;
                fw[u][v] = paino[u][v];
            }
        }
        bool ok = floyd_warshall(n, fw);
        bool sykliton = true;
        for (int lahto = 0; lahto < n; lahto++) {
            int e[MAX_N];
            if (!bellman_ford(n, paino, lahto, e)) {
                sykliton = false;       // sykli saavutettavissa lähdöstä
                continue;
            }
            for (int v = 0; ok && v < n; v++) {
                virheita += e[v] != fw[lahto][v];
            }
        }
        virheita += ok != sykliton;
        syklisia += !ok;
    }
    printf("vertailu Bellman-Fordiin: 300 graafia (%d negatiivista "
           "sykliä), %d virhettä\n", syklisia, virheita);
    return EXIT_SUCCESS;
}
