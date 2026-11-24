// Radix-2 FFT kahden potenssin pituuksille.
#pragma once
#include <complex.h>
#include <stdbool.h>
#include <stddef.h>

// @alku tyyppi
typedef struct {
    size_t n;                     // pituus, kahden potenssi
    double complex *kertoimet;    // n / 2 kiertokerrointa, kutsujan muistia
} fft_t;
// @loppu tyyppi

// Laskee kiertokertoimet. Palauttaa 0, tai -1, jos n ei ole kahden
// potenssi tai muisti puuttuu.
int fft_alusta(fft_t *s, size_t n, double complex *kertoimet);

// Muuntaa x:n paikallaan. Kaanteismuunnos jakaa n:lla.
void fft_suorita(const fft_t *s, double complex *x, bool kaanteinen);
