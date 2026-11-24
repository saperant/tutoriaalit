#include "prosessori.h"

#include <string.h>

#include "q15.h"

int prosessori_alusta(prosessori_t *p, const int16_t *h, size_t lkm,
                      int16_t *puskuri, int32_t vahvistus)
{
    if (p == NULL || h == NULL || puskuri == NULL || lkm == 0
        || vahvistus < 0 || vahvistus > 8 * 4096) {
        return -1;
    }
    *p = (prosessori_t){h, lkm, puskuri, 0, vahvistus, 0};
    memset(puskuri, 0, 2 * lkm * sizeof puskuri[0]);
    return 0;
}

// @alku lohko
void prosessori_lohko(prosessori_t *p, const int16_t *x, int16_t *y,
                      size_t n)
{
    for (size_t i = 0; i < n; i++) {
        p->paikka = p->paikka == 0 ? p->lkm - 1 : p->paikka - 1;
        p->viive[p->paikka] = p->viive[p->paikka + p->lkm] = x[i];
        const int16_t *v = &p->viive[p->paikka];
        int64_t kertyma = 0;                // Q.30, ei ylivuotoa
        for (size_t k = 0; k < p->lkm; k++) {
            kertyma += (int32_t)p->h[k] * v[k];
        }
        int64_t suodatettu = q15_saturoi(q15_pyorista(kertyma));
        int64_t tulos = (suodatettu * p->vahvistus + (1 << 11)) >> 12;
        int16_t ulos = q15_saturoi(tulos);
        p->saturaatiot += ulos != tulos;    // lasketaan, ei piiloteta
        y[i] = ulos;
    }
}
// @loppu lohko
