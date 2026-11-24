// Läpinäkymättömän tyypin kenttiin ei pääse käsiksi: kääntäjä tuntee
// vain nimen, ei rakennetta. Juuri tämä estää käyttäjää riippumasta
// toteutuksesta.
#include <stdio.h>
#include <stdlib.h>

// Otsaketiedostossa näkyy vain esittely, kuten joukko.h:ssa.
typedef struct laskuri Laskuri;
Laskuri *laskuri_luo(void);
int laskuri_arvo(const Laskuri *l);
void laskuri_tuhoa(Laskuri *l);

int main(void)
{
    Laskuri *l = laskuri_luo();
    if (l == nullptr) {
        return EXIT_FAILURE;
    }
#ifndef KORJATTU
    printf("arvo %d\n", l->arvo);   // virhe: epätäydellinen tyyppi
#else
    printf("arvo %d\n", laskuri_arvo(l));
#endif
    laskuri_tuhoa(l);
    return EXIT_SUCCESS;
}

// Toteutus on tavallisesti toisessa käännösyksikössä; tässä se on
// samassa tiedostossa, jotta esimerkki on yksi ohjelma.
struct laskuri {
    int arvo;
};

Laskuri *laskuri_luo(void)
{
    Laskuri *l = malloc(sizeof *l);
    if (l != nullptr) {
        l->arvo = 42;
    }
    return l;
}

int laskuri_arvo(const Laskuri *l)
{
    return l->arvo;
}

void laskuri_tuhoa(Laskuri *l)
{
    free(l);
}
