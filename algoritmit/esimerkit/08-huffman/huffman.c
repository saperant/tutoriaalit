// huffman.c: ahne Huffman-algoritmi pienellä binäärikeolla.
#include "huffman.h"

typedef struct {
    long paino;
    int pienin;         // alipuun pienin merkki: tasapelien ratkaisu
    int solmu;
} Alkio;

static bool ennen(Alkio a, Alkio b)
{
    return a.paino != b.paino ? a.paino < b.paino : a.pienin < b.pienin;
}

typedef struct {
    Alkio a[MERKKEJA];
    int n;
} Keko;

static void lisaa(Keko *k, Alkio x)
{
    int i = k->n++;
    while (i > 0 && ennen(x, k->a[(i - 1) / 2])) {
        k->a[i] = k->a[(i - 1) / 2];
        i = (i - 1) / 2;
    }
    k->a[i] = x;
}

static Alkio poista(Keko *k)
{
    Alkio pienin = k->a[0], x = k->a[--k->n];
    int i = 0;
    for (;;) {
        int c = 2 * i + 1;
        if (c >= k->n) {
            break;
        }
        if (c + 1 < k->n && ennen(k->a[c + 1], k->a[c])) {
            c++;
        }
        if (!ennen(k->a[c], x)) {
            break;
        }
        k->a[i] = k->a[c];
        i = c;
    }
    k->a[i] = x;
    return pienin;
}

static void koodit(Puu *p, int s, uint64_t bitit, int pituus)
{
    const Solmu *v = &p->solmut[s];
    if (v->vasen < 0) {
        // Yhden merkin syötteessäkin koodissa on oltava ainakin 1 bitti.
        p->koodi[v->merkki] = (Koodi){ bitit, pituus > 0 ? pituus : 1 };
        return;
    }
    koodit(p, v->vasen, bitit << 1, pituus + 1);
    koodit(p, v->oikea, (bitit << 1) | 1, pituus + 1);
}

// @alku rakenna
void huffman_rakenna(Puu *p, const long frekvenssi[MERKKEJA])
{
    Keko k = { .n = 0 };
    int solmuja = 0;
    for (int m = 0; m < MERKKEJA; m++) {
        p->koodi[m] = (Koodi){ 0, 0 };
        if (frekvenssi[m] > 0) {
            p->solmut[solmuja] = (Solmu){ -1, -1, m };
            lisaa(&k, (Alkio){ frekvenssi[m], m, solmuja++ });
        }
    }
    if (k.n == 0) {
        p->juuri = -1;
        return;
    }
    // Ahne askel: yhdistä kaksi kevyintä alipuuta, kunnes puita on yksi.
    while (k.n > 1) {
        Alkio a = poista(&k), b = poista(&k);
        p->solmut[solmuja] = (Solmu){ a.solmu, b.solmu, -1 };
        int pienin = a.pienin < b.pienin ? a.pienin : b.pienin;
        lisaa(&k, (Alkio){ a.paino + b.paino, pienin, solmuja++ });
    }
    p->juuri = k.a[0].solmu;
    koodit(p, p->juuri, 0, 0);
}
// @loppu rakenna
