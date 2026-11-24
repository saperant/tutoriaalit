// NLMS: painojen paivitys w += mu / (eps + |v|^2) * e * v.
#include "lms.h"

#include <string.h>

int nlms_alusta(nlms_t *s, size_t lkm, double mu, double *painot,
                double *puskuri)
{
    if (s == NULL || painot == NULL || puskuri == NULL || lkm == 0
        || !(mu > 0.0 && mu < 2.0)) {
        return -1;
    }
    *s = (nlms_t){painot, puskuri, lkm, 0, mu, 1e-8, 0.0};
    memset(painot, 0, lkm * sizeof painot[0]);
    memset(puskuri, 0, 2 * lkm * sizeof puskuri[0]);
    return 0;
}

// @alku askel
double nlms_askel(nlms_t *s, double x, double d, double *y)
{
    // Energia paivitetaan juoksevasti: pois vanhin, mukaan uusin.
    double vanhin = s->viive[s->paikka + s->lkm - 1];
    s->paikka = s->paikka == 0 ? s->lkm - 1 : s->paikka - 1;
    s->viive[s->paikka] = s->viive[s->paikka + s->lkm] = x;
    s->energia += x * x - vanhin * vanhin;
    if (s->energia < 0.0) {
        s->energia = 0.0;                   // pyoristys voi vieda alle 0
    }
    const double *v = &s->viive[s->paikka];
    double arvio = 0.0;
    for (size_t k = 0; k < s->lkm; k++) {
        arvio += s->w[k] * v[k];
    }
    double e = d - arvio;
    double askel = s->mu * e / (s->eps + s->energia);
    for (size_t k = 0; k < s->lkm; k++) {
        s->w[k] += askel * v[k];
    }
    if (y != NULL) {
        *y = arvio;
    }
    return e;
}
// @loppu askel
