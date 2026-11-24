// NLMS tunnistaa kaiun: painojen virhe pienenee naytteiden myota.
#include <math.h>
#include <stdio.h>

#include "lms.h"

#define LKM 8

// Toistettava kohina: xorshift ja Box-Muller.
static unsigned long long tila = 88172645463325252ull;

static double tasainen(void)
{
    tila ^= tila << 13;
    tila ^= tila >> 7;
    tila ^= tila << 17;
    return ((double)(tila >> 11) + 0.5) / 9007199254740992.0;  // (0, 1)
}

static double normaali(void)
{
    return sqrt(-2.0 * log(tasainen())) * cos(6.283185307179586 * tasainen());
}

int main(void)
{
    // @alku tunnistus
    static const double kaiku[LKM] = {0.5, -0.3, 0.2, 0.1, -0.05, 0.02,
                                      0.0, 0.01};
    double w[LKM], puskuri[2 * LKM], historia[LKM] = {0};
    nlms_t s;
    if (nlms_alusta(&s, LKM, 2.5, w, puskuri) != -1     // mu >= 2: hylkaa
        || nlms_alusta(&s, LKM, 0.5, w, puskuri) != 0) {
        fputs("nlms_alusta: vaara tulos\n", stderr);
        return 1;
    }
    for (int n = 1; n <= 5000; n++) {
        double x = normaali();
        for (int k = LKM - 1; k > 0; k--) {         // tuntematon jarjestelma
            historia[k] = historia[k - 1];
        }
        historia[0] = x;
        double d = 0.0;
        for (int k = 0; k < LKM; k++) {
            d += kaiku[k] * historia[k];
        }
        nlms_askel(&s, x, d + 0.001 * normaali(), NULL);
        if (n == 50 || n == 200 || n == 1000 || n == 5000) {
            double virhe = 0.0, teho = 0.0;
            for (int k = 0; k < LKM; k++) {
                virhe += (w[k] - kaiku[k]) * (w[k] - kaiku[k]);
                teho += kaiku[k] * kaiku[k];
            }
            printf("n = %4d: painojen virhe %6.1f dB\n", n,
                   10.0 * log10(virhe / teho));
        }
    }
    // @loppu tunnistus
    return 0;
}
