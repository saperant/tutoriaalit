// Ensimmäinen kiinteän pilkun luku: Q1.15 eli 16-bittinen murtoluku.
#include <math.h>
#include <stdint.h>
#include <stdio.h>

// @alku q15
// Q1.15: arvo = koodi / 2^15. Koodi on tavallinen int16_t.
#define Q15_SKAALA 32768.0

static int16_t q15(double x)
{
    double k = round(x * Q15_SKAALA);
    if (k > INT16_MAX) {
        k = INT16_MAX;            // 1,0 ei mahdu: suurin on 1 - 2^-15
    }
    if (k < INT16_MIN) {
        k = INT16_MIN;
    }
    return (int16_t)k;
}

static double arvo(int16_t koodi)
{
    return koodi / Q15_SKAALA;
}
// @loppu q15

int main(void)
{
    // @alku taulukko
    const double luvut[] = {0.5, -0.25, 0.3, -1.0, 1.0, 1e-5};
    printf("    luku   koodi  heksa       esitetty  virhe (LSB)\n");
    for (size_t i = 0; i < sizeof luvut / sizeof luvut[0]; i++) {
        int16_t k = q15(luvut[i]);
        double virhe = (arvo(k) - luvut[i]) * Q15_SKAALA;
        printf("%8.5f  %6d  0x%04x  %13.10f  %+7.3f\n", luvut[i], k,
               (unsigned)(uint16_t)k, arvo(k), virhe);
    }
    // @loppu taulukko
    return 0;
}
