// Bittitarkka Q1.15-FIR-suodatin: sama tulos kuin Python-mallissa.
#include <math.h>
#include <stdint.h>
#include <stdio.h>

#define TAPIT 15
#define NAYTTEET 200

// Alipäästön kertoimet Q1.15-muodossa (summa noin 1,0).
static const int16_t h[TAPIT] = {
    37, -128, -525, -667, 687, 4080, 8012, 9779,
    8012, 4080, 687, -667, -525, -128, 37,
};

// @alku syote
// Toistettava testisyöte: lineaarinen kongruenssigeneraattori.
static uint32_t tila = 12345;

static int16_t seuraava(void)
{
    tila = tila * 1103515245u + 12345u;
    return (int16_t)((int32_t)(tila >> 16) - 32768);   // tasajakauma
}
// @loppu syote

// @alku suodatin
// Kertymä 64 bitissä (riittää; laitteistossa 32 + 4 vartijabittiä).
// Q2.30 -> Q1.15: pyöristys lähimpään parilliseen ja saturaatio.
static int16_t suodata(const int16_t *x)        // x[0] on uusin
{
    int64_t kertyma = 0;
    for (int k = 0; k < TAPIT; k++) {
        kertyma += (int32_t)h[k] * x[k];
    }
    int64_t q = kertyma >= 0 ? kertyma >> 15 : ~(~kertyma >> 15);
    int64_t jaannos = kertyma & 0x7fff;
    if (jaannos > 0x4000 || (jaannos == 0x4000 && (q & 1))) {
        q += 1;
    }
    return (int16_t)(q > INT16_MAX ? INT16_MAX
                     : q < INT16_MIN ? INT16_MIN : q);
}
// @loppu suodatin

int main(void)
{
    // @alku ajo
    int16_t x[NAYTTEET + TAPIT - 1] = {0};      // alussa nollia
    for (int i = TAPIT - 1; i < NAYTTEET + TAPIT - 1; i++) {
        x[i] = seuraava();
    }
    uint32_t tarkiste = 2166136261u;            // FNV-1a ulostuloista
    double suurin_ero = 0.0;
    for (int n = 0; n < NAYTTEET; n++) {
        int16_t ikkuna[TAPIT];
        for (int k = 0; k < TAPIT; k++) {
            ikkuna[k] = x[n + TAPIT - 1 - k];
        }
        int16_t y = suodata(ikkuna);
        double viite = 0.0;                      // sama laskenta doublena
        for (int k = 0; k < TAPIT; k++) {
            viite += h[k] / 32768.0 * (ikkuna[k] / 32768.0);
        }
        double ero = fabs(y - viite * 32768.0);
        suurin_ero = ero > suurin_ero ? ero : suurin_ero;
        tarkiste = (tarkiste ^ (uint16_t)y) * 16777619u;
        if (n < 6) {
            printf("y[%d] = %6d\n", n, y);
        }
    }
    printf("tarkiste %08x\n", (unsigned)tarkiste);
    printf("suurin ero double-laskentaan %.3f LSB\n", suurin_ero);
    // @loppu ajo
    return 0;
}
