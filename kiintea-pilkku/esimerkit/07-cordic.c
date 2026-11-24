// CORDIC: sini ja kosini pelkillä yhteenlaskuilla ja siirroilla.
#include <math.h>
#include <stdint.h>
#include <stdio.h>

#define MURTO 29                 // kulmat ja tulokset Q3.29-muodossa
#define MAKS_ITER 24

static int32_t lattia(int32_t x, int k)
{
    return x >= 0 ? x >> k : ~(~x >> k);
}

static int32_t atan_taulu[MAKS_ITER];
static int32_t vahvistus[MAKS_ITER + 1];   // 1/K iteraatiomäärän mukaan

// Taulukot lasketaan kerran; laitteistossa ne ovat vakio-ROM.
static void alusta(void)
{
    double k = 1.0;
    vahvistus[0] = (int32_t)ldexp(1.0, MURTO);
    for (int i = 0; i < MAKS_ITER; i++) {
        atan_taulu[i] = (int32_t)lround(ldexp(atan(ldexp(1.0, -i)), MURTO));
        k *= sqrt(1.0 + ldexp(1.0, -2 * i));
        vahvistus[i + 1] = (int32_t)lround(ldexp(1.0 / k, MURTO));
    }
}

// @alku cordic
// Kiertomoodi: vektoria (1/K, 0) kierretään kulmaan z vakiokulmin
// ±atan(2^-i). Kierto 2^-i-kertoimella on pelkkä siirto ja summa.
static void cordic(int32_t z, int iter, int32_t *kos, int32_t *sin)
{
    int32_t x = vahvistus[iter], y = 0;
    for (int i = 0; i < iter; i++) {
        int32_t dx = lattia(y, i), dy = lattia(x, i);
        if (z >= 0) {
            x -= dx;
            y += dy;
            z -= atan_taulu[i];
        } else {
            x += dx;
            y -= dy;
            z += atan_taulu[i];
        }
    }
    *kos = x;
    *sin = y;
}
// @loppu cordic

int main(void)
{
    alusta();
    // @alku tarkkuus
    printf("iteraatiot  suurin virhe  tarkkoja bittejä\n");
    for (int iter = 4; iter <= 20; iter += 4) {
        double suurin = 0.0;
        for (int a = -90; a <= 90; a++) {          // asteina
            double kulma = a * acos(-1.0) / 180.0;
            int32_t c, s;
            cordic((int32_t)lround(ldexp(kulma, MURTO)), iter, &c, &s);
            double ec = fabs(ldexp(c, -MURTO) - cos(kulma));
            double es = fabs(ldexp(s, -MURTO) - sin(kulma));
            suurin = fmax(suurin, fmax(ec, es));
        }
        printf("%10d  %12.2e  %16.1f\n", iter, suurin, -log2(suurin));
    }
    // @loppu tarkkuus
    return 0;
}
