// Liukuluvun kentät: etumerkki, eksponentti ja mantissa.
#include <stdint.h>
#include <stdio.h>
#include <string.h>

// @alku purku
static void pura(const char *nimi, double x)
{
    uint64_t b;
    memcpy(&b, &x, sizeof b);          // bittikuvio sellaisenaan
    unsigned etumerkki = (unsigned)(b >> 63);
    unsigned eksponentti = (unsigned)((b >> 52) & 0x7ff);
    uint64_t mantissa = b & ((UINT64_C(1) << 52) - 1);
    printf("%-10s %u %4u %+6d 0x%013llx\n", nimi, etumerkki, eksponentti,
           (int)eksponentti - 1023, (unsigned long long)mantissa);
}
// @loppu purku

int main(void)
{
    printf("%-10s m  eks  -bias   mantissa\n", "arvo");
    pura("1.0", 1.0);
    pura("-2.5", -2.5);
    pura("0.1", 0.1);
    pura("1e300", 1e300);
    pura("min norm.", 0x1p-1022);
    pura("min subn.", 0x1p-1074);
    pura("0.0", 0.0);
    pura("-0.0", -0.0);
    pura("inf", 1.0 / 0.0);
    return 0;
}
