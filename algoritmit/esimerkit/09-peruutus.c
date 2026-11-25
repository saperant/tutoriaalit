// Peruuttava haku: ratkaisu rakennetaan valinta kerrallaan, ja haara
// hylätään heti, kun se ei voi johtaa sallittuun tai parempaan
// ratkaisuun. Sama retkireppu kuin esimerkissä 09-reppu.c.
#include <stdio.h>
#include <stdlib.h>

#include "satunnainen.h"

enum { MAX_N = 16 };

typedef struct {
    const char *nimi;
    int paino, arvo;
} Tavara;

// @alku haku
typedef enum { KAIKKI, PAINORAJA, ARVORAJA } Karsinta;

typedef struct {
    const Tavara *t;
    int n, raja;
    Karsinta karsinta;
    int loput[MAX_N + 1];       // loput[i] = tavaroiden i..n-1 arvot yhteensä
    int paras;                  // paras tähän mennessä löydetty arvo
    long solmuja;               // hakupuun solmut
} Haku;

// Tavarat 0..i-1 on päätetty; niiden paino ja arvo ovat parametreina.
static void hae(Haku *h, int i, int paino, int arvo)
{
    h->solmuja++;
    if (paino <= h->raja && arvo > h->paras) {
        h->paras = arvo;                // sallittu ja paras tähän asti
    }
    if (i == h->n) {
        return;
    }
    // Arvoraja: vaikka kaikki loput mahtuisivat, paras ei paranisi.
    if (h->karsinta == ARVORAJA && arvo + h->loput[i] <= h->paras) {
        return;
    }
    // Painoraja: liian painavaan haaraan ei mennä lainkaan.
    int p = h->t[i].paino;
    if (h->karsinta == KAIKKI || paino + p <= h->raja) {
        hae(h, i + 1, paino + p, arvo + h->t[i].arvo);     // i mukaan
    }
    hae(h, i + 1, paino, arvo);                             // i pois
}
// @loppu haku

static Haku aja(const Tavara *t, int n, int raja, Karsinta karsinta)
{
    Haku h = { .t = t, .n = n, .raja = raja, .karsinta = karsinta };
    for (int i = n - 1; i >= 0; i--) {
        h.loput[i] = h.loput[i + 1] + t[i].arvo;
    }
    hae(&h, 0, 0, 0);
    return h;
}

int main(void)
{
    const Tavara retki[] = {
        { "teltta", 25, 40 },   { "makuupussi", 15, 30 },
        { "retkikeitin", 8, 15 }, { "kamera", 6, 9 },
        { "kirja", 4, 4 },      { "sadetakki", 5, 12 },
        { "ruoka", 20, 35 },    { "vesipullo", 10, 20 },
    };
    const int n = sizeof retki / sizeof retki[0];
    static const char *const nimet[] = {
        "kaikki osajoukot", "painoraja karsii", "myös arvoraja karsii",
    };
    printf("%d tavaraa, raja 6,0 kg\n", n);
    for (Karsinta k = KAIKKI; k <= ARVORAJA; k++) {
        Haku h = aja(retki, n, 60, k);
        // Tulosteessa ä on kaksi tavua, joten leveys tasataan käsin.
        printf("%s:%*s %4ld solmua, paras arvo %d\n", nimet[k],
               k == ARVORAJA ? 0 : 4, "", h.solmuja, h.paras);
    }

    // Kaikkien kolmen on annettava sama optimi.
    Satunnainen s = { 29 };
    int virheita = 0;
    for (int kierros = 0; kierros < 300; kierros++) {
        int m = 1 + (int)satunnainen_alle(&s, 12);
        Tavara t[MAX_N];
        for (int i = 0; i < m; i++) {
            t[i] = (Tavara){ "", 1 + (int)satunnainen_alle(&s, 30),
                             (int)satunnainen_alle(&s, 50) };
        }
        int r = (int)satunnainen_alle(&s, 121);
        int a = aja(t, m, r, KAIKKI).paras;
        virheita += a != aja(t, m, r, PAINORAJA).paras ||
                    a != aja(t, m, r, ARVORAJA).paras;
    }
    printf("satunnaistesti: 300 tapausta, %d virhettä\n", virheita);
    return EXIT_SUCCESS;
}
