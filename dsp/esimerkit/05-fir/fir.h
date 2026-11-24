// FIR-suodin, jonka tila sailyy lohkojen valilla.
#pragma once
#include <stddef.h>

// @alku rakenne
typedef struct {
    const double *h;    // kertoimet h[0] ... h[lkm - 1], kutsujan muistia
    size_t lkm;
    double *viive;      // 2 * lkm alkiota: kaksoiskirjoitettu rengas
    size_t paikka;      // uusimman naytteen indeksi, 0 ... lkm - 1
} fir_t;
// @loppu rakenne

// Alustaa suotimen. puskurissa on oltava 2 * lkm alkiota. Palauttaa
// 0, tai -1, jos parametrit ovat virheelliset. Ei varaa muistia.
int fir_alusta(fir_t *s, const double *h, size_t lkm, double *puskuri);

// Nollaa viivelinjan (esim. katkon jalkeen).
void fir_nollaa(fir_t *s);

// Suodattaa n naytetta. x ja y saavat olla sama taulukko.
void fir_kasittele(fir_t *s, const double *x, double *y, size_t n);

// Sama symmetriselle suotimelle h[k] == h[lkm - 1 - k]: puolet
// kertolaskuista.
void fir_kasittele_symm(fir_t *s, const double *x, double *y, size_t n);
