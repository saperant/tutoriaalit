// Q1.15-kertolasku: tulo on Q2.30, ja takaisin Q1.15:een siirretään.
#include <stdint.h>
#include <stdio.h>

// @alku kerto
// Q1.15 * Q1.15 = Q2.30 (32 bittiä). Takaisin Q1.15:een: 15 bittiä
// oikealle pyöristäen ja saturoiden. Kerrottavat laajennetaan
// int32_t:ksi ennen kertolaskua, jotta tulo lasketaan 32 bitissä.
static int16_t q15_kerto(int16_t a, int16_t b)
{
    int32_t tulo = (int32_t)a * (int32_t)b;     // Q2.30
    int32_t pyor = (tulo + (1 << 14)) >> 15;    // pyöristys lähimpään
    if (pyor > INT16_MAX) {
        pyor = INT16_MAX;                        // vain -1 * -1
    }
    return (int16_t)pyor;
}
// @loppu kerto

int main(void)
{
    // @alku kokeet
    const int16_t pari[][2] = {
        {16384, 16384},     //  0.5  *  0.5
        {-8192, 24576},     // -0.25 *  0.75
        {32767, 32767},     // ~1    * ~1
        {-32768, -32768},   // -1    * -1 = 1, ei mahdu Q1.15:een
    };
    for (size_t i = 0; i < sizeof pari / sizeof pari[0]; i++) {
        int16_t a = pari[i][0], b = pari[i][1];
        int32_t q230 = (int32_t)a * b;
        printf("%9.6f * %9.6f: Q2.30 %11d, Q1.15 %6d = %9.6f\n",
               a / 32768.0, b / 32768.0, q230, q15_kerto(a, b),
               q15_kerto(a, b) / 32768.0);
    }
    // @loppu kokeet
    return 0;
}
