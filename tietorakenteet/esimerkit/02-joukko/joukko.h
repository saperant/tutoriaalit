// joukko.h: kokonaislukujoukon rajapinta.
//
// Joukko on läpinäkymätön: käyttäjä näkee vain tyypin nimen ja
// funktiot, ei toteutusta. Toteutus voidaan vaihtaa (lajiteltu
// taulukko, hajautustaulu, puu) ilman, että käyttäjän koodi muuttuu.
#ifndef JOUKKO_H
#define JOUKKO_H

#include <stddef.h>

// @alku rajapinta
typedef struct joukko Joukko;

typedef enum {
    JOUKKO_OK,          // alkio lisättiin tai poistettiin
    JOUKKO_ON_JO,       // lisättävä alkio oli jo joukossa
    JOUKKO_EI_OLE,      // poistettavaa alkiota ei ollut
    JOUKKO_MUISTI,      // muisti loppui; joukko on ennallaan
} JoukkoTila;

// Omistajuus: joukko_luo palauttaa kutsujan omistaman joukon, joka
// vapautetaan joukko_tuhoa-funktiolla. Alkiot kopioidaan joukkoon.
Joukko *joukko_luo(void);
void joukko_tuhoa(Joukko *j);

JoukkoTila joukko_lisaa(Joukko *j, int alkio);
JoukkoTila joukko_poista(Joukko *j, int alkio);
bool joukko_sisaltaa(const Joukko *j, int alkio);
size_t joukko_koko(const Joukko *j);

// Käy alkiot läpi kasvavassa järjestyksessä. Takaisinkutsu saa
// käyttäjän tiedon osoittimena; joukkoa ei saa muuttaa läpikäynnin
// aikana.
void joukko_kay_lapi(const Joukko *j,
                     void (*kasittele)(int alkio, void *tieto),
                     void *tieto);
// @loppu rajapinta

#endif
