// FIR-suodin kaksoiskirjoitetulla rengaspuskurilla.
#include "fir.h"

#include <string.h>

int fir_alusta(fir_t *s, const double *h, size_t lkm, double *puskuri)
{
    if (s == NULL || h == NULL || puskuri == NULL || lkm == 0) {
        return -1;
    }
    s->h = h;
    s->lkm = lkm;
    s->viive = puskuri;
    fir_nollaa(s);
    return 0;
}

void fir_nollaa(fir_t *s)
{
    memset(s->viive, 0, 2 * s->lkm * sizeof s->viive[0]);
    s->paikka = 0;
}

// @alku tyonna
// Uusin nayte kirjoitetaan kahteen paikkaan, i ja i + lkm. Silloin
// viimeiset lkm naytetta ovat aina perakkain alkaen indeksista i,
// eika sisasilmukassa tarvita jakojaannosta.
static const double *tyonna(fir_t *s, double x)
{
    s->paikka = s->paikka == 0 ? s->lkm - 1 : s->paikka - 1;
    s->viive[s->paikka] = x;
    s->viive[s->paikka + s->lkm] = x;
    return &s->viive[s->paikka];      // v[0] uusin, v[lkm - 1] vanhin
}
// @loppu tyonna

// @alku kasittele
void fir_kasittele(fir_t *s, const double *x, double *y, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        const double *v = tyonna(s, x[i]);
        double summa = 0.0;
        for (size_t k = 0; k < s->lkm; k++) {
            summa += s->h[k] * v[k];
        }
        y[i] = summa;
    }
}
// @loppu kasittele

// @alku symm
void fir_kasittele_symm(fir_t *s, const double *x, double *y, size_t n)
{
    const size_t puoli = s->lkm / 2;
    for (size_t i = 0; i < n; i++) {
        const double *v = tyonna(s, x[i]);
        double summa = 0.0;
        for (size_t k = 0; k < puoli; k++) {
            summa += s->h[k] * (v[k] + v[s->lkm - 1 - k]);
        }
        if (s->lkm % 2 == 1) {
            summa += s->h[puoli] * v[puoli];     // keskimmainen kerroin
        }
        y[i] = summa;
    }
}
// @loppu symm
