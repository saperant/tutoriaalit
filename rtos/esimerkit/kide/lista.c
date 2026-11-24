/* Ytimen listat. Kutsujan on oltava kriittisessä osiossa. */
#include "lista.h"

void lista_alusta(lista_t *lista) {
    lista->vartija.seuraava = &lista->vartija;
    lista->vartija.edellinen = &lista->vartija;
    lista->vartija.arvo = UINT32_MAX;
    lista->vartija.omistaja = NULL;
    lista->vartija.lista = lista;
    lista->pituus = 0;
}

void solmu_alusta(solmu_t *solmu, void *omistaja) {
    solmu->seuraava = NULL;
    solmu->edellinen = NULL;
    solmu->arvo = 0;
    solmu->omistaja = omistaja;
    solmu->lista = NULL;
}

/* Lisää solmun ennen solmua kohta. */
static void lisaa_ennen(lista_t *lista, solmu_t *kohta, solmu_t *solmu) {
    solmu->seuraava = kohta;
    solmu->edellinen = kohta->edellinen;
    kohta->edellinen->seuraava = solmu;
    kohta->edellinen = solmu;
    solmu->lista = lista;
    lista->pituus++;
}

void lista_lisaa_loppuun(lista_t *lista, solmu_t *solmu) {
    lisaa_ennen(lista, &lista->vartija, solmu);
}

// @alku jarjestys
void lista_lisaa_jarjestykseen(lista_t *lista, solmu_t *solmu,
                               uint32_t perus) {
    uint32_t avain = solmu->arvo - perus;
    solmu_t *kohta = lista->vartija.seuraava;
    while (kohta != &lista->vartija && kohta->arvo - perus <= avain) {
        kohta = kohta->seuraava;
    }
    lisaa_ennen(lista, kohta, solmu);
}
// @loppu jarjestys

void lista_poista(solmu_t *solmu) {
    lista_t *lista = solmu->lista;
    if (lista == NULL) {
        return;
    }
    solmu->edellinen->seuraava = solmu->seuraava;
    solmu->seuraava->edellinen = solmu->edellinen;
    solmu->seuraava = NULL;
    solmu->edellinen = NULL;
    solmu->lista = NULL;
    lista->pituus--;
}
