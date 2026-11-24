// Pienin virittävä puu: halvin kaarijoukko, joka yhdistää kaikki
// solmut. Kruskal lisää kaaria painojärjestyksessä ja hylkää syklin
// sulkevat (union-find kertoo sen); Prim kasvattaa yhtä puuta aina
// halvimmalla ulos lähtevällä kaarella. Molemmat ovat ahneita, ja
// niiden tuloksia verrataan satunnaisilla graafeilla.
#include <stdio.h>
#include <stdlib.h>

#include "satunnainen.h"

enum { MAX_N = 40, MAX_M = 800 };

typedef struct {
    int u, v, paino;
} Kaari;

// @alku unionfind
// Union-find pitää kirjaa erillisistä joukoista. Jokaisella joukolla on
// edustaja (puun juuri). Polun puolitus ja yhdistäminen koon mukaan
// tekevät operaatioista käytännössä vakioaikaisia.
typedef struct {
    int vanhempi[MAX_N], koko[MAX_N];
} Joukot;

static void joukot_alusta(Joukot *j, int n)
{
    for (int i = 0; i < n; i++) {
        j->vanhempi[i] = i;
        j->koko[i] = 1;
    }
}

static int etsi(Joukot *j, int x)
{
    while (j->vanhempi[x] != x) {
        j->vanhempi[x] = j->vanhempi[j->vanhempi[x]];   // puolitus
        x = j->vanhempi[x];
    }
    return x;
}

static bool yhdista(Joukot *j, int a, int b)   // false: jo samassa
{
    a = etsi(j, a);
    b = etsi(j, b);
    if (a == b) {
        return false;
    }
    if (j->koko[a] < j->koko[b]) {
        int t = a;
        a = b;
        b = t;
    }
    j->vanhempi[b] = a;             // pienempi puu suuremman alle
    j->koko[a] += j->koko[b];
    return true;
}
// @loppu unionfind

static int vertaa(const void *x, const void *y)
{
    const Kaari *a = x, *b = y;
    if (a->paino != b->paino) {
        return (a->paino > b->paino) - (a->paino < b->paino);
    }
    return a->u != b->u ? a->u - b->u : a->v - b->v;   // pieniä lukuja
}

// @alku kruskal
// Lajittelu O(m log m) hallitsee; union-find-operaatiot ovat halpoja.
static long kruskal(Kaari *k, int m, int n, Kaari *puu)
{
    static Joukot j;
    joukot_alusta(&j, n);
    qsort(k, (size_t)m, sizeof *k, vertaa);
    long summa = 0;
    int otettu = 0;
    for (int i = 0; i < m && otettu < n - 1; i++) {
        if (yhdista(&j, k[i].u, k[i].v)) {     // ei sulje sykliä
            puu[otettu++] = k[i];
            summa += k[i].paino;
        }
    }
    return otettu == n - 1 ? summa : -1;      // -1: ei yhtenäinen
}
// @loppu kruskal

// @alku prim
// Primin perusversio matriisilla, O(n^2): halvin[v] on halvin kaari
// puusta solmuun v. Kekoa käyttäen O(m log n), kuten Dijkstrassa.
static long prim(const int paino[MAX_N][MAX_N], int n)
{
    enum { EI = 1 << 30 };
    int halvin[MAX_N];
    bool puussa[MAX_N] = { false };
    for (int v = 0; v < n; v++) {
        halvin[v] = EI;
    }
    halvin[0] = 0;
    long summa = 0;
    for (int kierros = 0; kierros < n; kierros++) {
        int u = -1;
        for (int v = 0; v < n; v++) {
            if (!puussa[v] && (u < 0 || halvin[v] < halvin[u])) {
                u = v;
            }
        }
        if (halvin[u] == EI) {
            return -1;
        }
        puussa[u] = true;
        summa += halvin[u];
        for (int v = 0; v < n; v++) {
            if (!puussa[v] && paino[u][v] < halvin[v]) {
                halvin[v] = paino[u][v];
            }
        }
    }
    return summa;
}
// @loppu prim

int main(void)
{
    // Valokuitu kylien välille: mahdolliset kaivuureitit ja hinnat
    // (tuhansina euroina).
    static const char *const kyla[] = {
        "Aho", "Kangas", "Koski", "Mäki", "Niemi", "Salo",
    };
    Kaari reitit[] = {
        { 0, 1, 7 }, { 0, 2, 9 }, { 0, 5, 14 }, { 1, 2, 10 },
        { 1, 3, 15 }, { 2, 3, 11 }, { 2, 5, 2 }, { 3, 4, 6 },
        { 4, 5, 9 }, { 1, 4, 20 },
    };
    Kaari puu[MAX_N];
    long hinta = kruskal(reitit, 10, 6, puu);
    printf("hinta %ld tuhatta euroa\nkaivetaan:", hinta);
    for (int i = 0; i < 5; i++) {
        printf(" %s-%s", kyla[puu[i].u], kyla[puu[i].v]);
    }
    printf("\n");

    Satunnainen s = { 53 };
    int virheita = 0, epayhtenaisia = 0;
    static int paino[MAX_N][MAX_N];
    static Kaari k[MAX_M];
    for (int kierros = 0; kierros < 300; kierros++) {
        int n = 1 + (int)satunnainen_alle(&s, MAX_N);
        int m = 0;
        for (int u = 0; u < n; u++) {
            for (int v = 0; v < n; v++) {
                paino[u][v] = 1 << 30;
            }
        }
        for (int u = 0; u < n; u++) {
            for (int v = u + 1; v < n; v++) {
                if (satunnainen_alle(&s, 4) == 0) {     // n. 25 % pareista
                    int p = 1 + (int)satunnainen_alle(&s, 50);
                    k[m++] = (Kaari){ u, v, p };
                    paino[u][v] = paino[v][u] = p;
                }
            }
        }
        long a = kruskal(k, m, n, puu), b = prim(paino, n);
        epayhtenaisia += a < 0;
        virheita += a != b;
    }
    printf("Kruskal vs. Prim: 300 graafia (%d epäyhtenäistä), "
           "%d virhettä\n", epayhtenaisia, virheita);
    return EXIT_SUCCESS;
}
