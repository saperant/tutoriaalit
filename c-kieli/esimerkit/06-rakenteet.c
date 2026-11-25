#include <math.h>
#include <stdio.h>

// @alku maarittely
struct piste {
    double x;
    double y;
};

typedef struct {
    char nimi[32];
    struct piste sijainti;   // sisäkkäinen rakenne
    int vakiluku;
} Kaupunki;
// @loppu maarittely

// @alku solmu
// Rakenne voi sisältää osoittimen omaan tyyppiinsä.
struct solmu {
    int arvo;
    struct solmu *seuraava;   // nullptr: ketju päättyy
};
// @loppu solmu

// @alku funktiot
// Pieni rakenne voidaan välittää ja palauttaa arvona.
struct piste keskipiste(struct piste a, struct piste b)
{
    return (struct piste){(a.x + b.x) / 2, (a.y + b.y) / 2};
}

double etaisyys(struct piste a, struct piste b)
{
    return hypot(a.x - b.x, a.y - b.y);
}

// Suurempi rakenne välitetään osoittimena; const: ei muuteta.
void tulosta_kaupunki(const Kaupunki *k)
{
    printf("%s (%.1f, %.1f), %d asukasta\n", k->nimi,
           k->sijainti.x, k->sijainti.y, k->vakiluku);
}

void kasvata(Kaupunki *k, int muutto)
{
    k->vakiluku += muutto;   // k->kentta tarkoittaa (*k).kentta
}
// @loppu funktiot

int main(void)
{
    // @alku kaytto
    struct piste a = {0.0, 0.0};
    struct piste b = {.x = 3.0, .y = 4.0};
    struct piste k = keskipiste(a, b);
    printf("keskipiste (%.1f, %.1f), etäisyys %.1f\n",
           k.x, k.y, etaisyys(a, b));

    Kaupunki oulu = {
        .nimi = "Oulu",
        .sijainti = {.x = 25.5, .y = 65.0},
        .vakiluku = 216000,
    };
    Kaupunki kopio = oulu;   // sijoitus kopioi kaikki kentät
    kasvata(&oulu, 1000);
    tulosta_kaupunki(&oulu);
    tulosta_kaupunki(&kopio);

    double d = etaisyys((struct piste){1, 1}, (struct piste){4, 5});
    printf("yhdistetyillä literaaleilla: %.1f\n", d);
    // @loppu kaytto

    // @alku ketju
    struct solmu kolmas = {.arvo = 30, .seuraava = nullptr};
    struct solmu toinen = {.arvo = 20, .seuraava = &kolmas};
    struct solmu ensimmainen = {.arvo = 10, .seuraava = &toinen};

    printf("ketju:");
    for (const struct solmu *s = &ensimmainen; s != nullptr;
         s = s->seuraava) {
        printf(" %d", s->arvo);
    }
    printf("\n");
    // @loppu ketju
}
