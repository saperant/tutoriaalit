// joukko.c: joukko lajiteltuna dynaamisena taulukkona.
//
// Haku on puolitushaku, O(log n). Lisäys ja poisto siirtävät
// loppuosaa, O(n), mikä riittää pienille joukoille ja joukoille, joita
// luetaan paljon useammin kuin muutetaan.
#include "joukko.h"

#include <stdlib.h>
#include <string.h>

// @alku rakenne
struct joukko {
    int *alkiot;            // kasvavassa järjestyksessä, ei toistoja
    size_t koko;
    size_t kapasiteetti;
};
// @loppu rakenne

Joukko *joukko_luo(void)
{
    return calloc(1, sizeof(Joukko));
}

void joukko_tuhoa(Joukko *j)
{
    if (j != nullptr) {
        free(j->alkiot);
        free(j);
    }
}

// Ensimmäinen indeksi, jonka alkio on vähintään haettava.
static size_t ala_raja(const Joukko *j, int alkio)
{
    size_t vasen = 0, oikea = j->koko;
    while (vasen < oikea) {
        size_t keski = vasen + (oikea - vasen) / 2;
        if (j->alkiot[keski] < alkio) {
            vasen = keski + 1;
        } else {
            oikea = keski;
        }
    }
    return vasen;
}

bool joukko_sisaltaa(const Joukko *j, int alkio)
{
    size_t i = ala_raja(j, alkio);
    return i < j->koko && j->alkiot[i] == alkio;
}

// @alku lisaa
JoukkoTila joukko_lisaa(Joukko *j, int alkio)
{
    size_t i = ala_raja(j, alkio);
    if (i < j->koko && j->alkiot[i] == alkio) {
        return JOUKKO_ON_JO;
    }
    if (j->koko == j->kapasiteetti) {
        size_t uusi = j->kapasiteetti ? 2 * j->kapasiteetti : 8;
        int *alkiot = realloc(j->alkiot, uusi * sizeof *alkiot);
        if (alkiot == nullptr) {
            return JOUKKO_MUISTI;       // vanha taulukko on ennallaan
        }
        j->alkiot = alkiot;
        j->kapasiteetti = uusi;
    }
    memmove(&j->alkiot[i + 1], &j->alkiot[i],
            (j->koko - i) * sizeof *j->alkiot);
    j->alkiot[i] = alkio;
    j->koko++;
    return JOUKKO_OK;
}
// @loppu lisaa

JoukkoTila joukko_poista(Joukko *j, int alkio)
{
    size_t i = ala_raja(j, alkio);
    if (i == j->koko || j->alkiot[i] != alkio) {
        return JOUKKO_EI_OLE;
    }
    memmove(&j->alkiot[i], &j->alkiot[i + 1],
            (j->koko - i - 1) * sizeof *j->alkiot);
    j->koko--;
    return JOUKKO_OK;
}

size_t joukko_koko(const Joukko *j)
{
    return j->koko;
}

void joukko_kay_lapi(const Joukko *j,
                     void (*kasittele)(int alkio, void *tieto),
                     void *tieto)
{
    for (size_t i = 0; i < j->koko; i++) {
        kasittele(j->alkiot[i], tieto);
    }
}
