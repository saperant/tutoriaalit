// Vahvasti yhtenäiset komponentit Kosarajun algoritmilla: kaksi
// syvyyshakua. Ensimmäinen kirjaa solmut valmistumisjärjestykseen,
// toinen käy ne käänteisessä järjestyksessä läpi graafissa, jonka
// kaaret on käännetty. Tulos tarkistetaan saavutettavuusmatriisilla.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "satunnainen.h"

enum { MAX_N = 16 };

// @alku kosaraju
typedef struct {
    int n;
    bool kaari[MAX_N][MAX_N];   // pieni graafi: vierekkäisyysmatriisi
} Graafi;

typedef struct {
    const Graafi *g;
    bool kayty[MAX_N];
    int jarjestys[MAX_N], valmiita;     // 1. haku: valmistumisjärjestys
    int komponentti[MAX_N];             // 2. haku: solmun komponentti
} Tila;

static void valmistu(Tila *t, int u)            // kaaria pitkin
{
    t->kayty[u] = true;
    for (int v = 0; v < t->g->n; v++) {
        if (t->g->kaari[u][v] && !t->kayty[v]) {
            valmistu(t, v);
        }
    }
    t->jarjestys[t->valmiita++] = u;            // jälkijärjestys
}

static void merkitse(Tila *t, int u, int numero)   // kaaria vastaan
{
    t->komponentti[u] = numero;
    for (int v = 0; v < t->g->n; v++) {
        if (t->g->kaari[v][u] && t->komponentti[v] < 0) {
            merkitse(t, v, numero);
        }
    }
}

// Palauttaa komponenttien määrän; komponentti[u] on solmun u numero.
static int komponentit(const Graafi *g, int *komponentti)
{
    Tila t = { .g = g };
    for (int u = 0; u < g->n; u++) {
        if (!t.kayty[u]) {
            valmistu(&t, u);
        }
    }
    memset(t.komponentti, -1, sizeof t.komponentti);
    int maara = 0;
    for (int i = g->n - 1; i >= 0; i--) {       // viimeksi valmistunut ensin
        if (t.komponentti[t.jarjestys[i]] < 0) {
            merkitse(&t, t.jarjestys[i], maara++);
        }
    }
    memcpy(komponentti, t.komponentti, sizeof t.komponentti);
    return maara;
}
// @loppu kosaraju

int main(void)
{
    // @alku palvelut
    // Palvelujen kutsusuhteet: kaari a -> b, kun a kutsuu b:tä.
    static const char *const nimi[] = {
        "portti", "tilaus", "varasto", "laskutus", "ilmoitus", "loki",
        "raportti",
    };
    static const int kutsut[][2] = {
        { 0, 1 }, { 1, 2 }, { 2, 3 }, { 3, 1 },    // tilaus-varasto-laskutus
        { 1, 4 }, { 4, 5 }, { 3, 5 }, { 6, 5 }, { 6, 4 }, { 4, 6 },
    };
    Graafi g = { .n = 7 };
    for (size_t i = 0; i < sizeof kutsut / sizeof kutsut[0]; i++) {
        g.kaari[kutsut[i][0]][kutsut[i][1]] = true;
    }
    int k[MAX_N];
    int maara = komponentit(&g, k);
    printf("%d komponenttia:\n", maara);
    for (int c = 0; c < maara; c++) {
        printf("  %d:", c);
        for (int u = 0; u < g.n; u++) {
            if (k[u] == c) {
                printf(" %s", nimi[u]);
            }
        }
        printf("\n");
    }
    // @loppu palvelut

    // Vertailu: u ja v ovat samassa komponentissa täsmälleen silloin,
    // kun kumpikin on saavutettavissa toisesta.
    Satunnainen s = { 61 };
    int virheita = 0, yhden_solmun = 0, komponentteja = 0;
    for (int kierros = 0; kierros < 500; kierros++) {
        Graafi r = { .n = 1 + (int)satunnainen_alle(&s, MAX_N) };
        static bool yhteys[MAX_N][MAX_N];
        for (int u = 0; u < r.n; u++) {
            for (int v = 0; v < r.n; v++) {
                r.kaari[u][v] = u != v && satunnainen_alle(&s, 6) == 0;
                yhteys[u][v] = u == v || r.kaari[u][v];
            }
        }
        for (int w = 0; w < r.n; w++) {         // transitiivinen sulkeuma
            for (int u = 0; u < r.n; u++) {
                for (int v = 0; v < r.n; v++) {
                    yhteys[u][v] |= yhteys[u][w] && yhteys[w][v];
                }
            }
        }
        int m = komponentit(&r, k);
        komponentteja += m;
        yhden_solmun += m == r.n;
        for (int u = 0; u < r.n; u++) {
            for (int v = 0; v < r.n; v++) {
                virheita += (k[u] == k[v]) != (yhteys[u][v] && yhteys[v][u]);
            }
        }
    }
    printf("satunnaistesti: 500 graafia, %d komponenttia, %d graafissa "
           "ei syklejä, %d virhettä\n", komponentteja, yhden_solmun,
           virheita);
    return EXIT_SUCCESS;
}
