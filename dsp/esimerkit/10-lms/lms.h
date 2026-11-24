// NLMS-adaptiivinen FIR-suodin.
#pragma once
#include <stddef.h>

// @alku tyyppi
typedef struct {
    double *w;              // lkm painoa
    double *viive;          // 2 * lkm alkiota (kaksoiskirjoitettu rengas)
    size_t lkm, paikka;
    double mu, eps;         // askelkoko 0 < mu < 2 ja nollajaon esto
    double energia;         // juokseva sum v[k]^2 viivelinjassa
} nlms_t;
// @loppu tyyppi

// Painot ja viivelinja ovat kutsujan muistia. Palauttaa 0 tai -1.
int nlms_alusta(nlms_t *s, size_t lkm, double mu, double *painot,
                double *puskuri);

// Yksi askel: syote x, haluttu d. Palauttaa virheen e = d - y ja
// paivittaa painot. *y saa olla NULL.
double nlms_askel(nlms_t *s, double x, double d, double *y);
