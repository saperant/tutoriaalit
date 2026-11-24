// Yksöislinkitetty lista: tehtäväjono, joka pidetään prioriteetin
// mukaan järjestyksessä. Lisäys ja poisto keskeltä ovat O(1), kun
// paikka on löydetty, mutta paikan etsiminen on O(n).
#include <stdio.h>
#include <stdlib.h>

// @alku solmu
typedef struct solmu {
    int prioriteetti;
    const char *nimi;
    struct solmu *seuraava;
} Solmu;
// @loppu solmu

// @alku erikoistapaus
// Suoraviivainen versio: ensimmäinen solmu on erikoistapaus, koska sen
// edellä ei ole solmua, jonka seuraava-kenttää muuttaa.
static void poista_erikoistapauksin(Solmu **alku, const char *nimi)
{
    Solmu *s = *alku;
    if (s == nullptr) {
        return;
    }
    if (s->nimi == nimi) {
        *alku = s->seuraava;
        free(s);
        return;
    }
    while (s->seuraava != nullptr && s->seuraava->nimi != nimi) {
        s = s->seuraava;
    }
    if (s->seuraava != nullptr) {
        Solmu *pois = s->seuraava;
        s->seuraava = pois->seuraava;
        free(pois);
    }
}
// @loppu erikoistapaus

// @alku linkki
// Osoitin osoittimeen: p osoittaa siihen linkkiin, joka johtaa
// käsiteltävään solmuun – alun osoittimeen tai edellisen solmun
// seuraava-kenttään. Erikoistapaukset katoavat.
static void poista(Solmu **alku, const char *nimi)
{
    Solmu **p = alku;
    while (*p != nullptr && (*p)->nimi != nimi) {
        p = &(*p)->seuraava;
    }
    if (*p != nullptr) {
        Solmu *pois = *p;
        *p = pois->seuraava;
        free(pois);
    }
}

// Lisää prioriteetin mukaiseen paikkaan; samat prioriteetit
// saapumisjärjestyksessä (vakaa).
static bool lisaa(Solmu **alku, int prioriteetti, const char *nimi)
{
    Solmu *uusi = malloc(sizeof *uusi);
    if (uusi == nullptr) {
        return false;
    }
    uusi->prioriteetti = prioriteetti;
    uusi->nimi = nimi;
    Solmu **p = alku;
    while (*p != nullptr && (*p)->prioriteetti <= prioriteetti) {
        p = &(*p)->seuraava;
    }
    uusi->seuraava = *p;
    *p = uusi;
    return true;
}
// @loppu linkki

static void tulosta(const char *otsikko, const Solmu *s)
{
    printf("%-18s", otsikko);
    for (; s != nullptr; s = s->seuraava) {
        printf(" %s(%d)", s->nimi, s->prioriteetti);
    }
    printf("\n");
}

static void vapauta(Solmu *s)
{
    while (s != nullptr) {
        Solmu *seuraava = s->seuraava;
        free(s);
        s = seuraava;
    }
}

int main(void)
{
    Solmu *jono = nullptr;
    static const char *const nimet[] = {"varmuuskopio", "hälytys",
                                        "raportti", "päivitys",
                                        "loki"};
    const int prioriteetit[] = {3, 1, 5, 3, 9};
    for (int i = 0; i < 5; i++) {
        if (!lisaa(&jono, prioriteetit[i], nimet[i])) {
            vapauta(jono);
            return EXIT_FAILURE;
        }
    }
    tulosta("jono:", jono);
    poista(&jono, nimet[1]);            // ensimmäinen solmu
    poista(&jono, nimet[3]);            // keskeltä
    tulosta("poistojen jälkeen:", jono);
    poista_erikoistapauksin(&jono, nimet[4]);
    tulosta("loki pois:", jono);
    vapauta(jono);
    return EXIT_SUCCESS;
}
