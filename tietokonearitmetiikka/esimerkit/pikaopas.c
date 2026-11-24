// Pikaoppaan C-mallit.
#include <math.h>
#include <stdbit.h>
#include <stdckdint.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

// @alku tarkistettu
static bool varaa_koko(size_t n, size_t alkion_koko, size_t *koko)
{
    return !ckd_mul(koko, n, alkion_koko);    // false = ylivuoto
}
// @loppu tarkistettu

// @alku bitit
static uint32_t kentta(uint32_t s, unsigned alku, unsigned leveys)
{
    return (s >> alku) & ((1u << leveys) - 1u);     // leveys < 32
}

static int32_t laajenna(uint32_t x, unsigned n)     // n-bittinen etumerkki
{
    uint32_t m = 1u << (n - 1);
    return (int32_t)((x & ((m << 1) - 1u)) ^ m) - (int32_t)m;
}
// @loppu bitit

// @alku jako
static int lattiajaannos(int a, int b)              // tulos 0..b-1, b > 0
{
    int r = a % b;
    return r < 0 ? r + b : r;
}
// @loppu jako

// @alku liukuluku
static bool lahes(double a, double b, double suht, double abs_tol)
{
    return fabs(a - b) <= fmax(suht * fmax(fabs(a), fabs(b)), abs_tol);
}

static uint64_t bitit(double x)
{
    uint64_t b;
    memcpy(&b, &x, sizeof b);                 // ei osoitinmuunnosta
    return b;
}
// @loppu liukuluku

int main(void)
{
    size_t koko;
    printf("%d %d\n", varaa_koko(1000, 8, &koko),
           varaa_koko(SIZE_MAX / 2, 4, &koko));
    printf("%u %d\n", kentta(0x45b805dcu, 28, 4), laajenna(0xfff, 12));
    printf("%d %d\n", lattiajaannos(-30, 1440), lahes(0.1 + 0.2, 0.3,
                                                       1e-12, 0.0));
    printf("%016llx %u\n", (unsigned long long)bitit(1.0),
           stdc_count_ones(0xf0u));
    return 0;
}
