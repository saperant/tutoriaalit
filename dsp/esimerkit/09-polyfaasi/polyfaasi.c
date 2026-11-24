// Desimoija laskee vain sailytettavat ulostulot; interpoloija kayttaa
// polyfaasihaaroja eika kerro lisattyja nollia.
#include "polyfaasi.h"

#include <string.h>

int desimoija_alusta(desimoija_t *s, const double *h, size_t lkm, size_t M,
                     double *puskuri)
{
    if (s == NULL || h == NULL || puskuri == NULL || lkm == 0 || M == 0) {
        return -1;
    }
    *s = (desimoija_t){h, lkm, M, puskuri, 0, 0};
    memset(puskuri, 0, 2 * lkm * sizeof puskuri[0]);
    return 0;
}

// @alku desimoi
size_t desimoi(desimoija_t *s, const double *x, size_t n, double *y)
{
    size_t ulos = 0;
    for (size_t i = 0; i < n; i++) {
        s->paikka = s->paikka == 0 ? s->lkm - 1 : s->paikka - 1;
        s->viive[s->paikka] = s->viive[s->paikka + s->lkm] = x[i];
        if (s->vaihe == 0) {                 // vain joka M:s ulostulo
            const double *v = &s->viive[s->paikka];
            double summa = 0.0;
            for (size_t k = 0; k < s->lkm; k++) {
                summa += s->h[k] * v[k];
            }
            y[ulos++] = summa;
        }
        s->vaihe = (s->vaihe + 1) % s->M;
    }
    return ulos;
}
// @loppu desimoi

int interpoloija_alusta(interpoloija_t *s, const double *h, size_t lkm,
                        size_t L, double *puskuri)
{
    if (s == NULL || h == NULL || puskuri == NULL || L == 0 || lkm == 0
        || lkm % L != 0) {
        return -1;
    }
    *s = (interpoloija_t){h, lkm, L, puskuri, 0};
    memset(puskuri, 0, 2 * (lkm / L) * sizeof puskuri[0]);
    return 0;
}

// @alku interpoloi
// Haara p laskee ulostulon y[nL + p] = sum_j h[jL + p] x[n - j]: vain
// alkuperaiset naytteet, ei lisattyja nollia.
void interpoloi(interpoloija_t *s, const double *x, size_t n, double *y)
{
    const size_t haara = s->lkm / s->L;      // kertoimia haaraa kohti
    for (size_t i = 0; i < n; i++) {
        s->paikka = s->paikka == 0 ? haara - 1 : s->paikka - 1;
        s->viive[s->paikka] = s->viive[s->paikka + haara] = x[i];
        const double *v = &s->viive[s->paikka];
        for (size_t p = 0; p < s->L; p++) {
            double summa = 0.0;
            for (size_t j = 0; j < haara; j++) {
                summa += s->h[j * s->L + p] * v[j];
            }
            y[i * s->L + p] = summa;
        }
    }
}
// @loppu interpoloi
