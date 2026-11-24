// Desimoija ja interpoloija verrattuna suoraan toteutukseen.
#include <math.h>
#include <stdbool.h>
#include <stdio.h>

#include "polyfaasi.h"

#define LKM 48
#define KERROIN 4
#define PITUUS 1000
#define PII 3.14159265358979323846

// Suora toteutus vertailuksi: kaikki ulostulot taydella nopeudella.
static double suora_fir(const double *h, const double *x, size_t i)
{
    double summa = 0.0;
    for (size_t k = 0; k < LKM && k <= i; k++) {
        summa += h[k] * x[i - k];
    }
    return summa;
}

int main(void)
{
    // @alku kaytto
    double h[LKM];                     // Hann-ikkunoitu sinc, raja fs/8
    for (int k = 0; k < LKM; k++) {
        double t = k - (LKM - 1) / 2.0;
        double sinc = sin(PII * t / KERROIN) / (PII * t / KERROIN);
        h[k] = sinc / KERROIN * (0.5 - 0.5 * cos(2 * PII * (k + 0.5) / LKM));
    }
    static double x[PITUUS], y[PITUUS], viite[PITUUS * KERROIN];
    for (int i = 0; i < PITUUS; i++) {
        x[i] = sin(0.05 * i) + 0.3 * cos(0.31 * i);
    }
    double puskuri[2 * LKM];
    desimoija_t d;
    if (desimoija_alusta(&d, h, LKM, KERROIN, puskuri) != 0) {
        return 1;
    }
    size_t saatu = 0;
    for (size_t i = 0; i < PITUUS; i += 7) {           // lohkot 7 naytetta
        size_t koko = PITUUS - i < 7 ? PITUUS - i : 7;
        saatu += desimoi(&d, x + i, koko, y + saatu);
    }
    // @loppu kaytto

    // @alku vertaa
    bool samat = saatu == PITUUS / KERROIN;
    for (size_t m = 0; m < saatu; m++) {
        samat = samat && y[m] == suora_fir(h, x, m * KERROIN);
    }
    printf("desimoija: %zu ulostuloa, sama kuin suora: %s\n", saatu,
           samat ? "kylla" : "EI");

    double hi[LKM];                    // interpoloinnin vahvistus L
    for (int k = 0; k < LKM; k++) {
        hi[k] = KERROIN * h[k];
    }
    interpoloija_t ip;
    double ipuskuri[2 * LKM / KERROIN];
    if (interpoloija_alusta(&ip, hi, LKM, KERROIN, ipuskuri) != 0) {
        return 1;
    }
    interpoloi(&ip, x, PITUUS, viite);
    static double nollat[PITUUS * KERROIN];
    for (int i = 0; i < PITUUS; i++) {
        nollat[KERROIN * i] = x[i];                    // muut nollia
    }
    double ero = 0.0;
    for (size_t i = 0; i < PITUUS * KERROIN; i++) {
        ero = fmax(ero, fabs(viite[i] - suora_fir(hi, nollat, i)));
    }
    printf("interpoloija: ero suoraan alle 1e-15: %s\n",
           ero < 1e-15 ? "kylla" : "EI");
    printf("kertolaskuja syotenaytetta kohti:\n");
    printf("  desimoija %d (suora %d)\n", LKM / KERROIN, LKM);
    printf("  interpoloija %d (suora %d)\n", LKM, LKM * KERROIN);
    // @loppu vertaa
    return 0;
}
