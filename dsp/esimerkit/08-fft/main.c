// Oman FFT:n tarkistus: impulssi, sini, Parseval, paluu ja suora DFT.
#include <complex.h>
#include <math.h>
#include <stdio.h>

#include "fft.h"

#define N 1024
#define PII 3.14159265358979323846

int main(void)
{
    // @alku testit
    static double complex x[N], X[N], kertoimet[N / 2];
    fft_t fft;
    if (fft_alusta(&fft, 1000, kertoimet) != -1     // ei kahden potenssi
        || fft_alusta(&fft, N, kertoimet) != 0) {
        fputs("fft_alusta: vaara tulos\n", stderr);
        return 1;
    }

    // Sini taajuusbinissa 50: kaksi piikkia, korkeus N / 2.
    for (size_t i = 0; i < N; i++) {
        x[i] = X[i] = cos(2.0 * PII * 50.0 * (double)i / N);
    }
    fft_suorita(&fft, X, false);
    printf("|X[50]| = %.6f, |X[974]| = %.6f, |X[51]| < 1e-9: %s\n",
           cabs(X[50]), cabs(X[N - 50]), cabs(X[51]) < 1e-9 ? "kylla" : "EI");

    // Parseval: sum |x|^2 = sum |X|^2 / N.
    double ex = 0.0, eX = 0.0;
    for (size_t i = 0; i < N; i++) {
        ex += creal(x[i]) * creal(x[i]);
        eX += cabs(X[i]) * cabs(X[i]) / N;
    }
    printf("Parseval: %.6f = %.6f\n", ex, eX);

    // Suora DFT vertailuksi: O(N^2).
    double suurin = 0.0;
    for (size_t k = 0; k < N; k += 37) {
        double complex summa = 0.0;
        for (size_t i = 0; i < N; i++) {
            summa += x[i] * cexp(-2.0 * PII * I * (double)(k * i % N) / N);
        }
        suurin = fmax(suurin, cabs(summa - X[k]));
    }
    printf("ero suoraan DFT:hen alle 1e-9: %s\n",
           suurin < 1e-9 ? "kylla" : "EI");

    fft_suorita(&fft, X, true);
    double paluu = 0.0;
    for (size_t i = 0; i < N; i++) {
        paluu = fmax(paluu, cabs(X[i] - x[i]));
    }
    printf("kaanteismuunnos palauttaa, virhe alle 1e-12: %s\n",
           paluu < 1e-12 ? "kylla" : "EI");
    printf("kompleksikertolaskuja: FFT %d, suora DFT %d\n",
           N / 2 * 10, N * N);               // (N / 2) log2 N, log2 N = 10
    // @loppu testit
    return 0;
}
