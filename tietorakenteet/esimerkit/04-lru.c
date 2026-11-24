// LRU-välimuisti (least recently used): kaksoislinkitetty rengaslista
// tunnussolmulla pitää sivut käyttöjärjestyksessä, ja indeksitaulukko
// löytää sivun solmun O(1)-ajassa. Osuma siirtää solmun listan
// alkuun, ja täydestä välimuistista poistetaan listan viimeinen.
#include <stdio.h>
#include <stdlib.h>

enum { SIVUJA = 16, KAPASITEETTI = 3 };

// @alku rakenne
typedef struct solmu {
    struct solmu *edellinen, *seuraava;
    int sivu;
} Solmu;

typedef struct {
    Solmu tunnus;               // ei dataa; tunnus.seuraava = uusin
    Solmu *indeksi[SIVUJA];     // sivu -> solmu tai nullptr
    int koko;
} Lru;

static void irrota(Solmu *s)
{
    s->edellinen->seuraava = s->seuraava;
    s->seuraava->edellinen = s->edellinen;
}

static void lisaa_alkuun(Lru *l, Solmu *s)
{
    s->edellinen = &l->tunnus;
    s->seuraava = l->tunnus.seuraava;
    l->tunnus.seuraava->edellinen = s;
    l->tunnus.seuraava = s;
}
// @loppu rakenne

// @alku hae
// Palauttaa true osumalla. Huti lataa sivun ja tarvittaessa poistaa
// vanhimman. Kaikki operaatiot ovat O(1): ei hakuja listasta.
static bool hae(Lru *l, int sivu)
{
    Solmu *s = l->indeksi[sivu];
    if (s != nullptr) {
        irrota(s);
        lisaa_alkuun(l, s);
        return true;
    }
    if (l->koko == KAPASITEETTI) {
        s = l->tunnus.edellinen;        // vanhin
        irrota(s);
        l->indeksi[s->sivu] = nullptr;
    } else {
        s = malloc(sizeof *s);
        if (s == nullptr) {
            exit(EXIT_FAILURE);
        }
        l->koko++;
    }
    s->sivu = sivu;
    l->indeksi[sivu] = s;
    lisaa_alkuun(l, s);
    return false;
}
// @loppu hae

int main(void)
{
    Lru l = {.koko = 0};
    l.tunnus.seuraava = l.tunnus.edellinen = &l.tunnus;   // tyhjä rengas

    const int viitteet[] = {1, 2, 3, 1, 4, 2, 5, 1, 2, 3};
    int osumia = 0;
    for (size_t i = 0; i < sizeof viitteet / sizeof viitteet[0]; i++) {
        bool osui = hae(&l, viitteet[i]);
        osumia += osui;
        printf("sivu %d: %-5s välimuisti:", viitteet[i],
               osui ? "osuma" : "huti");
        for (Solmu *s = l.tunnus.seuraava; s != &l.tunnus;
             s = s->seuraava) {
            printf(" %d", s->sivu);
        }
        printf("\n");
    }
    printf("osumia %d / %zu\n", osumia,
           sizeof viitteet / sizeof viitteet[0]);
    while (l.tunnus.seuraava != &l.tunnus) {
        Solmu *s = l.tunnus.seuraava;
        irrota(s);
        free(s);
    }
    return EXIT_SUCCESS;
}
