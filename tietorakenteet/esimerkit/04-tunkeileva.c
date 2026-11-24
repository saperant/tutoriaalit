// Tunkeileva (intrusive) lista: linkit ovat itse tietueen kentissä,
// eivät erillisissä solmuissa. Sama tietue voi olla monessa listassa
// yhtä aikaa ilman lisävarauksia; Linuxin ydin käyttää tätä mallia
// (list_head).
#include <stddef.h>
#include <stdio.h>

// @alku linkki
typedef struct linkki {
    struct linkki *edellinen, *seuraava;
} Linkki;

// Tietueen osoite sen jäsenen osoitteesta.
#define SISALTAVA(osoitin, tyyppi, jasen) \
    ((tyyppi *)((char *)(osoitin) - offsetof(tyyppi, jasen)))

static void lista_alusta(Linkki *tunnus)
{
    tunnus->edellinen = tunnus->seuraava = tunnus;
}

static void lista_loppuun(Linkki *tunnus, Linkki *l)
{
    l->seuraava = tunnus;
    l->edellinen = tunnus->edellinen;
    tunnus->edellinen->seuraava = l;
    tunnus->edellinen = l;
}

static void lista_irrota(Linkki *l)
{
    l->edellinen->seuraava = l->seuraava;
    l->seuraava->edellinen = l->edellinen;
    l->edellinen = l->seuraava = l;
}
// @loppu linkki

// @alku tietue
typedef struct {
    int tunniste;
    const char *nimi;
    Linkki kaikki;          // kaikkien prosessien lista
    Linkki valmiit;         // ajovalmiiden jono
} Prosessi;
// @loppu tietue

static void tulosta_valmiit(const Linkki *tunnus)
{
    printf("ajovalmiit:");
    // @alku lapikaynti
    for (const Linkki *l = tunnus->seuraava; l != tunnus; l = l->seuraava) {
        const Prosessi *p = SISALTAVA(l, const Prosessi, valmiit);
        printf(" %s(%d)", p->nimi, p->tunniste);
    }
    // @loppu lapikaynti
    printf("\n");
}

int main(void)
{
    Prosessi prosessit[] = {
        {1, "init", {}, {}}, {7, "sshd", {}, {}}, {12, "cron", {}, {}},
        {30, "httpd", {}, {}},
    };
    Linkki kaikki, valmiit;
    lista_alusta(&kaikki);
    lista_alusta(&valmiit);
    for (size_t i = 0; i < sizeof prosessit / sizeof prosessit[0]; i++) {
        lista_loppuun(&kaikki, &prosessit[i].kaikki);
        lista_loppuun(&valmiit, &prosessit[i].valmiit);
    }
    tulosta_valmiit(&valmiit);

    // sshd jää odottamaan: pois ajovalmiista, mutta yhä kaikkien listassa.
    lista_irrota(&prosessit[1].valmiit);
    tulosta_valmiit(&valmiit);

    int prosesseja = 0;
    for (Linkki *l = kaikki.seuraava; l != &kaikki; l = l->seuraava) {
        prosesseja++;
    }
    printf("prosesseja kaikkiaan: %d, ei yhtään malloc-kutsua\n",
           prosesseja);
    return 0;
}
