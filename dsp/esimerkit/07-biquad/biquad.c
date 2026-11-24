// Biquad-ketju: suunnittelu, suodatus ja taajuusvaste.
#include "biquad.h"

#include <math.h>
#include <string.h>

#define PII 3.14159265358979323846

static int tarkista(double f0, double q, double fs)
{
    return fs > 0.0 && f0 > 0.0 && f0 < fs / 2.0 && q > 0.0 ? 0 : -1;
}

// @alku alipaasto
int biquad_alipaasto(biquad_t *k, double f0, double q, double fs)
{
    if (k == NULL || tarkista(f0, q, fs) != 0) {
        return -1;
    }
    double w0 = 2.0 * PII * f0 / fs;
    double alfa = sin(w0) / (2.0 * q), c = cos(w0);
    double a0 = 1.0 + alfa;
    k->b0 = (1.0 - c) / 2.0 / a0;
    k->b1 = (1.0 - c) / a0;
    k->b2 = k->b0;
    k->a1 = -2.0 * c / a0;
    k->a2 = (1.0 - alfa) / a0;
    return 0;
}
// @loppu alipaasto

int biquad_korostus(biquad_t *k, double f0, double q, double db, double fs)
{
    if (k == NULL || tarkista(f0, q, fs) != 0) {
        return -1;
    }
    double A = pow(10.0, db / 40.0), w0 = 2.0 * PII * f0 / fs;
    double alfa = sin(w0) / (2.0 * q), c = cos(w0);
    double a0 = 1.0 + alfa / A;
    k->b0 = (1.0 + alfa * A) / a0;
    k->b1 = -2.0 * c / a0;
    k->b2 = (1.0 - alfa * A) / a0;
    k->a1 = -2.0 * c / a0;
    k->a2 = (1.0 - alfa / A) / a0;
    return 0;
}

int sos_alusta(sos_t *s, const biquad_t *lohkot, size_t lkm, double *tila,
               sos_muoto_t muoto)
{
    if (s == NULL || lohkot == NULL || tila == NULL || lkm == 0) {
        return -1;
    }
    *s = (sos_t){lohkot, lkm, tila, muoto};
    sos_nollaa(s);
    return 0;
}

void sos_nollaa(sos_t *s)
{
    memset(s->tila, 0, 4 * s->lkm * sizeof s->tila[0]);
}

// @alku df1
// Suoramuoto I: tila on kaksi edellista syotetta ja ulostuloa.
static double df1(const biquad_t *k, double *t, double x)
{
    double y = k->b0 * x + k->b1 * t[0] + k->b2 * t[1]
               - k->a1 * t[2] - k->a2 * t[3];
    t[1] = t[0];
    t[0] = x;
    t[3] = t[2];
    t[2] = y;
    return y;
}
// @loppu df1

// @alku df2t
// Transponoitu suoramuoto II: kaksi tilamuuttujaa.
static double df2t(const biquad_t *k, double *t, double x)
{
    double y = k->b0 * x + t[0];
    t[0] = k->b1 * x - k->a1 * y + t[1];
    t[1] = k->b2 * x - k->a2 * y;
    return y;
}
// @loppu df2t

// @alku kasittele
void sos_kasittele(sos_t *s, const double *x, double *y, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        double v = x[i];
        for (size_t j = 0; j < s->lkm; j++) {      // lohkot sarjassa
            double *t = &s->tila[4 * j];
            v = s->muoto == SOS_DF1 ? df1(&s->lohkot[j], t, v)
                                    : df2t(&s->lohkot[j], t, v);
        }
        y[i] = v;
    }
}
// @loppu kasittele

double complex sos_vaste(const biquad_t *lohkot, size_t lkm, double f,
                         double fs)
{
    double complex z1 = cexp(-I * 2.0 * PII * f / fs);    // z^-1
    double complex H = 1.0;
    for (size_t j = 0; j < lkm; j++) {
        const biquad_t *k = &lohkot[j];
        H *= (k->b0 + k->b1 * z1 + k->b2 * z1 * z1)
             / (1.0 + k->a1 * z1 + k->a2 * z1 * z1);
    }
    return H;
}
