// Käännösjärjestys riippuvuuksista: topologinen järjestys Kahnin
// algoritmilla ja syklin etsintä syvyyshaulla. Kaari u -> v tarkoittaa,
// että u on tehtävä ennen v:tä. Satunnaistesti tarkistaa, että järjestys
// noudattaa kaikkia kaaria ja että menetelmät ovat syklistä samaa mieltä.
#include <stdio.h>
#include <stdlib.h>

#include "satunnainen.h"

enum { MAX = 16 };

typedef struct {
    int n;
    bool kaari[MAX][MAX];       // pienelle graafille riittää matriisi
} Graafi;

// @alku kahn
// Toistetaan: valitaan solmu, jolla ei ole käsittelemättömiä edeltäjiä.
// Jos solmuja jää yli, niiden välillä on sykli. Aika O(n + m)
// vierekkäisyyslistoilla, matriisilla O(n^2).
static int kahn(const Graafi *g, int *jarjestys)
{
    int sisaan[MAX] = { 0 }, jono[MAX], alku = 0, loppu = 0;
    for (int u = 0; u < g->n; u++) {
        for (int v = 0; v < g->n; v++) {
            sisaan[v] += g->kaari[u][v];
        }
    }
    for (int v = 0; v < g->n; v++) {
        if (sisaan[v] == 0) {
            jono[loppu++] = v;
        }
    }
    while (alku < loppu) {
        int u = jono[alku++];
        jarjestys[alku - 1] = u;
        for (int v = 0; v < g->n; v++) {
            if (g->kaari[u][v] && --sisaan[v] == 0) {
                jono[loppu++] = v;
            }
        }
    }
    return alku;                // < n, jos graafissa on sykli
}
// @loppu kahn

// @alku sykli
// Syvyyshaku kolmella värillä: valkoinen = käymätön, harmaa = pinossa,
// musta = valmis. Kaari harmaaseen solmuun sulkee syklin.
typedef enum { VALKOINEN, HARMAA, MUSTA } Vari;

static int syvyyshaku(const Graafi *g, int u, Vari *vari, int *edeltaja)
{
    vari[u] = HARMAA;
    for (int v = 0; v < g->n; v++) {
        if (!g->kaari[u][v]) {
            continue;
        }
        if (vari[v] == HARMAA) {
            edeltaja[v] = u;    // sykli v -> ... -> u -> v
            return v;
        }
        if (vari[v] == VALKOINEN) {
            edeltaja[v] = u;
            int s = syvyyshaku(g, v, vari, edeltaja);
            if (s >= 0) {
                return s;
            }
        }
    }
    vari[u] = MUSTA;
    return -1;
}

// Palauttaa syklin pituuden ja kirjoittaa sen solmut taulukkoon, tai 0.
static int etsi_sykli(const Graafi *g, int *sykli)
{
    Vari vari[MAX] = { VALKOINEN };
    int edeltaja[MAX];
    for (int u = 0; u < g->n; u++) {
        if (vari[u] == VALKOINEN) {
            int s = syvyyshaku(g, u, vari, edeltaja);
            if (s >= 0) {
                int k = 0, v = s;
                do {            // kuljetaan edeltäjiä takaisin s:ään
                    sykli[k++] = v;
                    v = edeltaja[v];
                } while (v != s);
                for (int i = 0; i < k / 2; i++) {   // oikeaan suuntaan
                    int t = sykli[i];
                    sykli[i] = sykli[k - 1 - i];
                    sykli[k - 1 - i] = t;
                }
                return k;
            }
        }
    }
    return 0;
}
// @loppu sykli

static const char *const nimet[] = {
    "asetukset.h", "lista.c", "lista.o", "main.c", "main.o",
    "ohjelma", "testit.c", "testit.o", "testaa",
};

static void kaari(Graafi *g, int u, int v)
{
    g->kaari[u][v] = true;
}

int main(void)
{
    // @alku projekti
    Graafi g = { .n = 9 };
    kaari(&g, 0, 2);            // asetukset.h -> lista.o
    kaari(&g, 0, 4);            // asetukset.h -> main.o
    kaari(&g, 1, 2);            // lista.c -> lista.o
    kaari(&g, 3, 4);            // main.c -> main.o
    kaari(&g, 2, 5);            // lista.o -> ohjelma
    kaari(&g, 4, 5);            // main.o -> ohjelma
    kaari(&g, 6, 7);            // testit.c -> testit.o
    kaari(&g, 2, 8);            // lista.o -> testaa
    kaari(&g, 7, 8);            // testit.o -> testaa
    // @loppu projekti
    int jarj[MAX], sykli[MAX];
    int k = kahn(&g, jarj);
    printf("käännösjärjestys:\n");
    for (int i = 0; i < k; i++) {
        printf("%s%s", nimet[jarj[i]], i % 5 == 4 || i == k - 1 ? "\n"
                                                               : " ");
    }

    kaari(&g, 5, 0);            // virhe: ohjelma -> asetukset.h
    printf("syklin jälkeen järjestykseen mahtuu %d/%d\n",
           kahn(&g, jarj), g.n);
    int pituus = etsi_sykli(&g, sykli);
    printf("sykli:");
    for (int i = 0; i < pituus; i++) {
        printf(" %s ->", nimet[sykli[i]]);
    }
    printf(" %s\n", nimet[sykli[0]]);

    Satunnainen s = { 41 };
    int virheita = 0, syklisia = 0;
    for (int kierros = 0; kierros < 1000; kierros++) {
        Graafi r = { .n = 1 + (int)satunnainen_alle(&s, MAX) };
        int kaaria = (int)satunnainen_alle(&s, (uint32_t)(2 * r.n));
        for (int e = 0; e < kaaria; e++) {
            int u = (int)satunnainen_alle(&s, (uint32_t)r.n);
            int v = (int)satunnainen_alle(&s, (uint32_t)r.n);
            r.kaari[u][v] = true;
        }
        int maara = kahn(&r, jarj), kohta[MAX];
        int sp = etsi_sykli(&r, sykli);
        syklisia += sp > 0;
        if ((maara == r.n) != (sp == 0)) {
            virheita++;         // menetelmät eri mieltä syklistä
        }
        for (int i = 0; i < sp; i++) {
            virheita += !r.kaari[sykli[i]][sykli[(i + 1) % sp]];
        }
        if (maara == r.n) {
            for (int i = 0; i < r.n; i++) {
                kohta[jarj[i]] = i;
            }
            for (int u = 0; u < r.n; u++) {
                for (int v = 0; v < r.n; v++) {
                    virheita += r.kaari[u][v] && kohta[u] >= kohta[v];
                }
            }
        }
    }
    printf("satunnaistesti: 1000 graafia (%d syklisiä), %d virhettä\n",
           syklisia, virheita);
    return EXIT_SUCCESS;
}
