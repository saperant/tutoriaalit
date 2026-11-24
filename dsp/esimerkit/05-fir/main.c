// FIR-suotimen kaytto: lohkoittain kasittely ja symmetrinen muoto.
#include <math.h>
#include <stdbool.h>
#include <stdio.h>

#include "fir.h"
#include "kertoimet.h"

#define FS 8000.0
#define PITUUS 4000
#define PII 3.14159265358979323846   // PII ei kuulu C-standardiin

// Amplitudi taajuudella f: korrelaatio kompleksiseen siniin.
static double amplitudi(const double *y, size_t n, double f)
{
    double re = 0.0, im = 0.0;
    for (size_t i = 0; i < n; i++) {
        re += y[i] * cos(2.0 * PII * f / FS * (double)i);
        im -= y[i] * sin(2.0 * PII * f / FS * (double)i);
    }
    return 2.0 * hypot(re, im) / (double)n;
}

int main(void)
{
    // @alku syote
    static double x[PITUUS], kerralla[PITUUS], lohkoittain[PITUUS];
    for (size_t i = 0; i < PITUUS; i++) {
        double t = (double)i / FS;
        x[i] = sin(2.0 * PII * 300.0 * t)
               + 0.5 * sin(2.0 * PII * 3000.0 * t);
    }
    // @loppu syote

    // @alku kaytto
    double puskuri[2 * KERTOIMIA];       // ei mallocia: kutsujan muisti
    fir_t suodin;
    if (fir_alusta(&suodin, kertoimet, KERTOIMIA, puskuri) != 0) {
        fputs("fir_alusta epaonnistui\n", stderr);
        return 1;
    }
    fir_kasittele(&suodin, x, kerralla, PITUUS);

    // Sama signaali vaihtelevan kokoisina lohkoina.
    fir_nollaa(&suodin);
    static const size_t koot[] = {1, 7, 64, 3, 250, 31, 32};
    size_t alku = 0;
    for (size_t j = 0; alku < PITUUS; j++) {
        size_t koko = koot[j % (sizeof koot / sizeof koot[0])];
        if (koko > PITUUS - alku) {
            koko = PITUUS - alku;
        }
        fir_kasittele(&suodin, x + alku, lohkoittain + alku, koko);
        alku += koko;
    }
    // @loppu kaytto

    // @alku tarkistus
    bool samat = true;
    for (size_t i = 0; i < PITUUS; i++) {
        samat = samat && kerralla[i] == lohkoittain[i];   // bitilleen
    }
    double symm[PITUUS], suurin = 0.0;
    fir_nollaa(&suodin);
    fir_kasittele_symm(&suodin, x, symm, PITUUS);
    for (size_t i = 0; i < PITUUS; i++) {
        suurin = fmax(suurin, fabs(symm[i] - kerralla[i]));
    }
    const double *y = kerralla + 800;    // transientti ohi, 120 jaksoa
    for (int j = 0; j < 2; j++) {
        double f = j == 0 ? 300.0 : 3000.0;
        double db = 20.0 * log10(amplitudi(y, 3200, f)
                                 / amplitudi(x + 800, 3200, f));
        printf("%4.0f Hz: vahvistus %7.2f dB\n", f, db);
    }
    printf("lohkoittain == kerralla: %s\n", samat ? "kylla" : "EI");
    printf("symmetrinen muoto, ero alle 1e-15: %s\n",
           suurin < 1e-15 ? "kylla" : "EI");
    printf("kertolaskuja naytteelle: suora %d, symmetrinen %d\n",
           KERTOIMIA, (KERTOIMIA + 1) / 2);
    // @loppu tarkistus
    return 0;
}
