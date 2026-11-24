// Binäärikeko prioriteettijonona: ajastinjono, josta otetaan aina
// aikaisin erääntyvä tapahtuma. Keko on taulukko, jossa solmun i
// lapset ovat 2i+1 ja 2i+2, eikä osoittimia tarvita.
#include <stdio.h>
#include <stdlib.h>

#include "satunnainen.h"

// @alku rakenne
typedef struct {
    long aika;                  // erääntymisaika, ms
    int tunniste;
} Tapahtuma;

typedef struct {
    Tapahtuma *t;
    size_t koko, kapasiteetti;
    long vaihtoja;              // mittausta varten
} Keko;

// Pienempi aika ensin; tasapeleissä pienempi tunniste, jotta järjestys
// on määrätty eikä riipu lisäysjärjestyksestä.
static bool ennen(Tapahtuma a, Tapahtuma b)
{
    return a.aika < b.aika || (a.aika == b.aika && a.tunniste < b.tunniste);
}

static void vaihda(Keko *k, size_t i, size_t j)
{
    Tapahtuma apu = k->t[i];
    k->t[i] = k->t[j];
    k->t[j] = apu;
    k->vaihtoja++;
}
// @loppu rakenne

// @alku nosta
static void nosta(Keko *k, size_t i)        // sift up
{
    while (i > 0 && ennen(k->t[i], k->t[(i - 1) / 2])) {
        vaihda(k, i, (i - 1) / 2);
        i = (i - 1) / 2;
    }
}

static void laske(Keko *k, size_t i)        // sift down
{
    for (;;) {
        size_t pienin = i, v = 2 * i + 1, o = 2 * i + 2;
        if (v < k->koko && ennen(k->t[v], k->t[pienin])) {
            pienin = v;
        }
        if (o < k->koko && ennen(k->t[o], k->t[pienin])) {
            pienin = o;
        }
        if (pienin == i) {
            return;
        }
        vaihda(k, i, pienin);
        i = pienin;
    }
}

static bool keko_lisaa(Keko *k, Tapahtuma t)
{
    if (k->koko == k->kapasiteetti) {
        size_t uusi = k->kapasiteetti ? 2 * k->kapasiteetti : 16;
        Tapahtuma *data = realloc(k->t, uusi * sizeof *data);
        if (data == nullptr) {
            return false;
        }
        k->t = data;
        k->kapasiteetti = uusi;
    }
    k->t[k->koko++] = t;
    nosta(k, k->koko - 1);
    return true;
}

static Tapahtuma keko_ota(Keko *k)          // kutsujan vastuu: koko > 0
{
    Tapahtuma pienin = k->t[0];
    k->t[0] = k->t[--k->koko];
    laske(k, 0);
    return pienin;
}
// @loppu nosta

// @alku kekoutus
// Valmiista taulukosta keoksi alhaalta ylös: lehdet ovat jo kekoja,
// joten aloitetaan viimeisestä sisäsolmusta. Työtä on O(n), koska
// useimmat solmut ovat lähellä lehtiä eivätkä laskeudu kauas.
static void kekouta(Keko *k)
{
    for (size_t i = k->koko / 2; i-- > 0;) {
        laske(k, i);
    }
}
// @loppu kekoutus

int main(void)
{
    // Ajastimet erääntymisjärjestykseen.
    Keko k = {};
    const Tapahtuma ajastimet[] = {
        {500, 1}, {120, 2}, {900, 3}, {120, 4}, {30, 5}, {600, 6},
    };
    for (size_t i = 0; i < sizeof ajastimet / sizeof ajastimet[0]; i++) {
        if (!keko_lisaa(&k, ajastimet[i])) {
            return EXIT_FAILURE;
        }
    }
    printf("järjestys, ms(#tunniste):");
    while (k.koko > 0) {
        Tapahtuma t = keko_ota(&k);
        printf(" %ld(#%d)", t.aika, t.tunniste);
    }
    printf("\n");

    // @alku vertailu
    // n lisäystä yksitellen vs. sama data kekoutettuna kerralla, kun
    // ajat ovat satunnaisia ja kun ne tulevat laskevassa järjestyksessä
    // (jokainen uusi nousee juureen asti).
    enum { N = 100000 };
    static Tapahtuma data[N];
    Satunnainen s = {5};
    bool samat = true;
    for (int laskeva = 0; laskeva <= 1; laskeva++) {
        for (int i = 0; i < N; i++) {
            data[i] = (Tapahtuma){laskeva ? N - i
                                  : (long)satunnainen_alle(&s, N), i};
        }
        Keko yksitellen = {};
        for (int i = 0; i < N; i++) {
            if (!keko_lisaa(&yksitellen, data[i])) {
                return EXIT_FAILURE;
            }
        }
        Keko kerralla = {data, N, N, 0};    // keko lainaa taulukon
        kekouta(&kerralla);
        printf("%-10s %d lisäystä: %7ld vaihtoa, kekoutus: %6ld vaihtoa\n",
               laskeva ? "laskeva:" : "satunnais:", N, yksitellen.vaihtoja,
               kerralla.vaihtoja);
        while (yksitellen.koko > 0) {       // sama järjestys molemmista
            Tapahtuma a = keko_ota(&yksitellen), b = keko_ota(&kerralla);
            samat = samat && a.aika == b.aika && a.tunniste == b.tunniste;
        }
        free(yksitellen.t);
    }
    // @loppu vertailu
    printf("otot samassa järjestyksessä: %s\n", samat ? "kyllä" : "EI");
    free(k.t);
    return samat ? EXIT_SUCCESS : EXIT_FAILURE;
}
