/* Kahteen suuntaan linkitetty rengaslista vartijasolmulla.
 *
 * Solmu on upotettu omistajaansa (tehtävän ohjauslohkoon), joten
 * listaan lisääminen ei varaa muistia: kaikki ytimen toiminnot ovat
 * vakioaikaisia lukuun ottamatta järjestykseen lisäämistä, jonka
 * kesto riippuu listan pituudesta. FreeRTOSin list.c toimii samoin. */
#ifndef LISTA_H
#define LISTA_H

#include <stddef.h>
#include <stdint.h>

// @alku tyypit
typedef struct lista lista_t;

typedef struct solmu {
    struct solmu *seuraava;
    struct solmu *edellinen;
    uint32_t arvo;        /* järjestysavain: herätystikki tai prioriteetti */
    void *omistaja;       /* tehtävä, jonka osa solmu on */
    lista_t *lista;       /* lista, jossa solmu on; NULL = ei missään */
} solmu_t;

struct lista {
    solmu_t vartija;      /* tyhjässä listassa osoittaa itseensä */
    uint32_t pituus;
};
// @loppu tyypit

void lista_alusta(lista_t *lista);
void solmu_alusta(solmu_t *solmu, void *omistaja);
void lista_lisaa_loppuun(lista_t *lista, solmu_t *solmu);
/* Lisää nousevaan järjestykseen avaimen (arvo - perus) mukaan;
 * yhtä suurten joukossa viimeiseksi. Perusarvo tekee vertailusta
 * turvallisen tikkilaskurin pyörähtäessä ympäri. */
void lista_lisaa_jarjestykseen(lista_t *lista, solmu_t *solmu,
                               uint32_t perus);
void lista_poista(solmu_t *solmu);

static inline solmu_t *lista_ensimmainen(const lista_t *lista) {
    return lista->pituus == 0 ? NULL : lista->vartija.seuraava;
}

#endif
