// Monitaajuussuotimet: desimoija ja polyfaasi-interpoloija.
#pragma once
#include <stddef.h>

// @alku tyypit
typedef struct {
    const double *h;
    size_t lkm, M;          // kertoimet ja harvennuskerroin
    double *viive;          // 2 * lkm alkiota
    size_t paikka, vaihe;   // vaihe: syotteita viime ulostulosta
} desimoija_t;

typedef struct {
    const double *h;
    size_t lkm, L;          // lkm:n on oltava L:n monikerta
    double *viive;          // 2 * lkm / L alkiota
    size_t paikka;
} interpoloija_t;
// @loppu tyypit

int desimoija_alusta(desimoija_t *s, const double *h, size_t lkm, size_t M,
                     double *puskuri);
// Kasittelee n syotetta ja palauttaa tuotettujen ulostulojen maaran
// (enintaan n / M + 1). Lohkon pituus saa olla mika tahansa.
size_t desimoi(desimoija_t *s, const double *x, size_t n, double *y);

int interpoloija_alusta(interpoloija_t *s, const double *h, size_t lkm,
                        size_t L, double *puskuri);
// Kasittelee n syotetta ja kirjoittaa n * L ulostuloa.
void interpoloi(interpoloija_t *s, const double *x, size_t n, double *y);
