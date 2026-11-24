// Pikaoppaan apufunktiot: Q1.15-perusoperaatiot C23:lla.
#include <stdint.h>
#include <stdio.h>

// @alku perus
static int16_t sat16(int64_t x)                       // saturaatio
{
    return (int16_t)(x > INT16_MAX ? INT16_MAX
                     : x < INT16_MIN ? INT16_MIN : x);
}

static int64_t lattia(int64_t x, int k)               // >> siirrettävästi
{
    return x >= 0 ? x >> k : ~(~x >> k);
}

static int64_t parilliseen(int64_t x, int k)          // konvergentti
{
    int64_t q = lattia(x, k), r = x & ((INT64_C(1) << k) - 1);
    int64_t puoli = INT64_C(1) << (k - 1);
    return q + (r > puoli || (r == puoli && (q & 1)));
}

static int16_t q15_kerto(int16_t a, int16_t b)        // Q1.15 * Q1.15
{
    return sat16(parilliseen((int32_t)a * b, 15));
}

static int32_t laajenna(uint32_t x, int bitit)       // etumerkki
{
    uint32_t m = UINT32_C(1) << (bitit - 1);
    return (int32_t)((x & ((m << 1) - 1)) ^ m) - (int32_t)m;
}
// @loppu perus

int main(void)
{
    printf("%d %d %d %d\n", sat16(40000), q15_kerto(16384, -16384),
           (int)parilliseen(6, 2), laajenna(0xfff, 12));
    return 0;
}
