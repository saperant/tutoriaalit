// Lyhimmät reitit painotetussa graafissa: Dijkstran algoritmi
// binäärikeolla ja vertailukohtana Bellman-Ford. Esimerkkinä tieverkko
// (likimääräiset etäisyydet kilometreinä), sitten satunnaistesti ja
// lopuksi negatiivinen paino, joka rikkoo Dijkstran.
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

#include "satunnainen.h"

enum { MAX_N = 64, MAX_M = 512 };
static const long AARETON = LONG_MAX / 4;

// Kaarilista solmuittain: ensimmainen[u] on u:n ensimmäinen kaari, ja
// kaaret on ketjutettu kentällä seuraava (ks. Tietorakenteet, luku 10).
typedef struct {
    int kohde, paino, seuraava;
} Kaari;

typedef struct {
    int n, m;
    int ensimmainen[MAX_N];
    Kaari kaari[MAX_M];
} Graafi;

static void alusta(Graafi *g, int n)
{
    g->n = n;
    g->m = 0;
    for (int u = 0; u < n; u++) {
        g->ensimmainen[u] = -1;
    }
}

static void lisaa_kaari(Graafi *g, int u, int v, int paino)
{
    g->kaari[g->m] = (Kaari){ v, paino, g->ensimmainen[u] };
    g->ensimmainen[u] = g->m++;
}

// Binäärikeko pareista (etäisyys, solmu). Samaa solmua voi olla keossa
// useita kertoja; vanhentuneet parit ohitetaan poistettaessa.
typedef struct {
    long etaisyys;
    int solmu;
} Pari;

typedef struct {
    Pari a[MAX_M + 1];
    int n;
} Keko;

static void keko_lisaa(Keko *k, Pari x)
{
    int i = k->n++;
    while (i > 0 && x.etaisyys < k->a[(i - 1) / 2].etaisyys) {
        k->a[i] = k->a[(i - 1) / 2];
        i = (i - 1) / 2;
    }
    k->a[i] = x;
}

static Pari keko_poista(Keko *k)
{
    Pari pienin = k->a[0], x = k->a[--k->n];
    int i = 0;
    for (int c = 1; c < k->n; c = 2 * i + 1) {
        if (c + 1 < k->n && k->a[c + 1].etaisyys < k->a[c].etaisyys) {
            c++;
        }
        if (k->a[c].etaisyys >= x.etaisyys) {
            break;
        }
        k->a[i] = k->a[c];
        i = c;
    }
    k->a[i] = x;
    return pienin;
}

// @alku dijkstra
// Kun solmu poistetaan keosta ensimmäisen kerran, sen etäisyys on lopullinen:
// kaikki muut keon reitit ovat vähintään yhtä pitkiä, eivätkä
// ei-negatiiviset kaaret voi lyhentää niitä. Aika O((n + m) log n).
static void dijkstra(const Graafi *g, int lahto, long *d, int *edeltaja)
{
    static Keko k;
    bool valmis[MAX_N] = { false };
    for (int u = 0; u < g->n; u++) {
        d[u] = AARETON;
        edeltaja[u] = -1;
    }
    d[lahto] = 0;
    k.n = 0;
    keko_lisaa(&k, (Pari){ 0, lahto });
    while (k.n > 0) {
        int u = keko_poista(&k).solmu;
        if (valmis[u]) {
            continue;               // vanhentunut pari
        }
        valmis[u] = true;
        for (int e = g->ensimmainen[u]; e >= 0; e = g->kaari[e].seuraava) {
            int v = g->kaari[e].kohde;
            if (d[u] + g->kaari[e].paino < d[v]) {     // relaksaatio
                d[v] = d[u] + g->kaari[e].paino;
                edeltaja[v] = u;
                keko_lisaa(&k, (Pari){ d[v], v });
            }
        }
    }
}
// @loppu dijkstra

// @alku bellman
// Bellman-Ford: relaksoidaan kaikki kaaret n - 1 kierrosta. Lyhin reitti
// käyttää enintään n - 1 kaarta, joten negatiivisetkin painot käyvät.
// Jos n:skin kierros vielä parantaa, graafissa on negatiivinen sykli.
// Aika O(n m). Palauttaa false negatiivisen syklin löytyessä.
static bool bellman_ford(const Graafi *g, int lahto, long *d)
{
    for (int u = 0; u < g->n; u++) {
        d[u] = AARETON;
    }
    d[lahto] = 0;
    for (int kierros = 0; kierros < g->n; kierros++) {
        bool muuttui = false;
        for (int u = 0; u < g->n; u++) {
            for (int e = g->ensimmainen[u]; e >= 0;
                 e = g->kaari[e].seuraava) {
                const Kaari *k = &g->kaari[e];
                if (d[u] < AARETON && d[u] + k->paino < d[k->kohde]) {
                    d[k->kohde] = d[u] + k->paino;
                    muuttui = true;
                }
            }
        }
        if (!muuttui) {
            return true;
        }
    }
    return false;
}
// @loppu bellman

static void tie(Graafi *g, int u, int v, int km)    // kumpaankin suuntaan
{
    lisaa_kaari(g, u, v, km);
    lisaa_kaari(g, v, u, km);
}

static void tulosta_reitti(const char *const *nimi, const int *edeltaja,
                           int v)
{
    if (edeltaja[v] >= 0) {
        tulosta_reitti(nimi, edeltaja, edeltaja[v]);
        printf(" -> ");
    }
    printf("%s", nimi[v]);
}

int main(void)
{
    // @alku tieverkko
    enum { HKI, TKU, TRE, HML, LTI, KVL, JKL, MLI, KUO, PRI, N };
    static const char *const nimi[] = {
        "Helsinki", "Turku", "Tampere", "Hämeenlinna", "Lahti",
        "Kouvola", "Jyväskylä", "Mikkeli", "Kuopio", "Pori",
    };
    static Graafi g;
    alusta(&g, N);
    tie(&g, HKI, TKU, 165);
    tie(&g, HKI, HML, 100);
    tie(&g, HKI, LTI, 105);
    tie(&g, HKI, KVL, 135);
    tie(&g, TKU, TRE, 160);
    tie(&g, TKU, PRI, 140);
    tie(&g, HML, TRE, 75);
    tie(&g, LTI, TRE, 130);
    tie(&g, LTI, JKL, 170);
    tie(&g, LTI, MLI, 125);
    tie(&g, KVL, MLI, 90);
    tie(&g, TRE, JKL, 150);
    tie(&g, TRE, PRI, 110);
    tie(&g, JKL, KUO, 145);
    tie(&g, MLI, KUO, 160);
    // @loppu tieverkko
    long d[MAX_N], d2[MAX_N];
    int edeltaja[MAX_N];
    dijkstra(&g, HKI, d, edeltaja);
    for (int v = 0; v < N; v++) {
        if (v == KUO || v == PRI || v == JKL) {
            printf("%4ld km  ", d[v]);
            tulosta_reitti(nimi, edeltaja, v);
            printf("\n");
        }
    }

    Satunnainen s = { 47 };
    int virheita = 0;
    for (int kierros = 0; kierros < 200; kierros++) {
        int n = 1 + (int)satunnainen_alle(&s, MAX_N);
        int m = (int)satunnainen_alle(&s, MAX_M);
        alusta(&g, n);
        for (int e = 0; e < m; e++) {
            lisaa_kaari(&g, (int)satunnainen_alle(&s, (uint32_t)n),
                        (int)satunnainen_alle(&s, (uint32_t)n),
                        (int)satunnainen_alle(&s, 100));
        }
        dijkstra(&g, 0, d, edeltaja);
        bellman_ford(&g, 0, d2);
        for (int v = 0; v < n; v++) {
            virheita += d[v] != d2[v];
        }
    }
    printf("vertailu Bellman-Fordiin: 200 graafia, %d virhettä\n", virheita);

    // @alku negatiivinen
    // A -> B 2, A -> C 3, C -> B -2, B -> D 1. Oikea etäisyys D:hen on 2
    // (A, C, B, D), mutta Dijkstra on jo julistanut B:n valmiiksi.
    alusta(&g, 4);
    lisaa_kaari(&g, 0, 1, 2);
    lisaa_kaari(&g, 0, 2, 3);
    lisaa_kaari(&g, 2, 1, -2);
    lisaa_kaari(&g, 1, 3, 1);
    dijkstra(&g, 0, d, edeltaja);
    bellman_ford(&g, 0, d2);
    printf("negatiivinen kaari: D:hen Dijkstra %ld, Bellman-Ford %ld\n",
           d[3], d2[3]);
    lisaa_kaari(&g, 1, 2, 1);           // sykli C -> B -> C, paino -1
    printf("negatiivinen sykli: Bellman-Ford %s\n",
           bellman_ford(&g, 0, d2) ? "ei havaitse" : "havaitsee");
    // @loppu negatiivinen
    return EXIT_SUCCESS;
}
