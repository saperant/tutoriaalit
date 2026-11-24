// Muunnos liukuluvusta kiinteään pilkkuun ja muodosta toiseen.
#include <math.h>
#include <stdint.h>
#include <stdio.h>

// @alku muunnos
// Liukuluku -> Qm.n (n murtobittiä, bitit-leveä etumerkillinen),
// pyöristys lähimpään ja saturaatio. Palauttaa koodin int32_t:nä.
static int32_t kiintea(double x, int bitit, int n)
{
    double suurin = ldexp(1.0, bitit - 1) - 1.0;
    double pienin = -ldexp(1.0, bitit - 1);
    double k = nearbyint(ldexp(x, n));     // x * 2^n, pyöristys
    if (k > suurin) {
        k = suurin;
    }
    if (k < pienin) {
        k = pienin;
    }
    return (int32_t)k;
}

static double liuku(int32_t koodi, int n)
{
    return ldexp((double)koodi, -n);       // koodi / 2^n
}
// @loppu muunnos

int main(void)
{
    // @alku esimerkit
    const double x = 3.14159265358979;
    printf("pi Q4.12:  koodi %6d, arvo %.6f\n",
           kiintea(x, 16, 12), liuku(kiintea(x, 16, 12), 12));
    printf("pi Q8.8:   koodi %6d, arvo %.6f\n",
           kiintea(x, 16, 8), liuku(kiintea(x, 16, 8), 8));
    printf("pi Q1.15:  koodi %6d, arvo %.6f (saturoitui)\n",
           kiintea(x, 16, 15), liuku(kiintea(x, 16, 15), 15));
    // @loppu esimerkit

    // @alku vaihto
    // Q4.12 -> Q1.15: kolme murtobittiä lisää eli siirto vasemmalle.
    // Mahtuu vain, jos arvo on välillä [-1, 1).
    const int32_t a = kiintea(0.75, 16, 12);
    const int32_t b = kiintea(2.5, 16, 12);
    printf("0.75 Q4.12 %5d -> Q1.15 %6d\n", a, a * 8);
    printf("2.50 Q4.12 %5d -> Q1.15 %6d ei mahdu int16:een\n",
           b, b * 8);
    // @loppu vaihto
    return 0;
}
