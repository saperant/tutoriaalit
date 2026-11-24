/* Kiinteän kokoisten lohkojen muistipooli. Varaus ja vapautus ovat
 * vakioaikaisia, eikä pooli pirstoudu, koska kaikki lohkot ovat
 * samankokoisia. Laskeva semafori laskee vapaat lohkot, joten varaus
 * voi odottaa vapautumista aikarajan kanssa. */
#ifndef POOLI_H
#define POOLI_H

#include "kide.h"

// @alku tyyppi
typedef struct lohko {
    struct lohko *seuraava;   /* vain vapaalistassa */
} lohko_t;

typedef struct {
    uint8_t *muisti;
    size_t lohkon_koko;
    size_t lohkoja;
    lohko_t *vapaat;          /* vapaiden lohkojen lista */
    StaticSemaphore_t laskuri_tila;
    SemaphoreHandle_t laskuri;
} pooli_t;
// @loppu tyyppi

void pooli_alusta(pooli_t *pooli, void *muisti, size_t lohkon_koko,
                  size_t lohkoja);
void *pooli_varaa(pooli_t *pooli, TickType_t aikaraja);
void pooli_vapauta(pooli_t *pooli, void *osoite);
size_t pooli_vapaana(pooli_t *pooli);

#endif
