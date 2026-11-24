// Toisen asteen lohkojen (biquad) ketju kahdessa suoramuodossa.
#pragma once
#include <complex.h>
#include <stddef.h>

// @alku tyypit
typedef struct {
    double b0, b1, b2, a1, a2;      // normitettu: a0 = 1
} biquad_t;

typedef enum { SOS_DF1, SOS_DF2T } sos_muoto_t;

typedef struct {
    const biquad_t *lohkot;         // kutsujan muistia
    size_t lkm;
    double *tila;                   // 4 * lkm alkiota
    sos_muoto_t muoto;
} sos_t;
// @loppu tyypit

// Kertoimet R. Bristow-Johnsonin kaavoilla (bilineaarimuunnos ja
// esivaaristys). Palauttaa 0, tai -1, jos parametrit ovat virheelliset.
int biquad_alipaasto(biquad_t *k, double f0, double q, double fs);
int biquad_korostus(biquad_t *k, double f0, double q, double db,
                    double fs);

int sos_alusta(sos_t *s, const biquad_t *lohkot, size_t lkm, double *tila,
               sos_muoto_t muoto);
void sos_nollaa(sos_t *s);
void sos_kasittele(sos_t *s, const double *x, double *y, size_t n);

// Taajuusvaste H(e^{i 2 pi f / fs}) suoraan kertoimista.
double complex sos_vaste(const biquad_t *lohkot, size_t lkm, double f,
                         double fs);
