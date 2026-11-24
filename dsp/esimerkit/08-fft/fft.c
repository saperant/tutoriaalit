// Iteratiivinen radix-2-FFT: bittien kaanto ja perhoset.
#include "fft.h"

#include <math.h>

#define PII 3.14159265358979323846

// @alku alusta
int fft_alusta(fft_t *s, size_t n, double complex *kertoimet)
{
    if (s == NULL || kertoimet == NULL || n < 2 || (n & (n - 1)) != 0) {
        return -1;
    }
    // Jokainen kerroin lasketaan suoraan: rekursio w *= w1 kerryttaisi
    // pyoristysvirhetta pitkissa muunnoksissa.
    for (size_t k = 0; k < n / 2; k++) {
        double kulma = -2.0 * PII * (double)k / (double)n;
        kertoimet[k] = cos(kulma) + I * sin(kulma);
    }
    s->n = n;
    s->kertoimet = kertoimet;
    return 0;
}
// @loppu alusta

// @alku kaanto
static void kaanna_bitit(double complex *x, size_t n)
{
    for (size_t i = 1, j = 0; i < n; i++) {
        size_t bitti = n >> 1;
        for (; j & bitti; bitti >>= 1) {    // j + 1 bitit kaannettyina
            j ^= bitti;
        }
        j ^= bitti;
        if (i < j) {
            double complex t = x[i];
            x[i] = x[j];
            x[j] = t;
        }
    }
}
// @loppu kaanto

// @alku perhoset
void fft_suorita(const fft_t *s, double complex *x, bool kaanteinen)
{
    const size_t n = s->n;
    kaanna_bitit(x, n);
    for (size_t pituus = 2; pituus <= n; pituus <<= 1) {
        const size_t askel = n / pituus;    // kerroinhyppy tasolla
        for (size_t alku = 0; alku < n; alku += pituus) {
            for (size_t k = 0; k < pituus / 2; k++) {
                double complex w = s->kertoimet[k * askel];
                if (kaanteinen) {
                    w = conj(w);
                }
                double complex a = x[alku + k];
                double complex b = w * x[alku + k + pituus / 2];
                x[alku + k] = a + b;
                x[alku + k + pituus / 2] = a - b;
            }
        }
    }
    if (kaanteinen) {
        for (size_t i = 0; i < n; i++) {
            x[i] /= (double)n;
        }
    }
}
// @loppu perhoset
