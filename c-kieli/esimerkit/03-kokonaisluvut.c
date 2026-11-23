#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

int main(void)
{
    // @alku stdint
    int32_t tasan32 = -123456;
    uint8_t tavu = 200;
    uint64_t suuri = 18'000'000'000'000'000'000u;   // C23: erottimet
    printf("%" PRId32 " %" PRIu8 " %" PRIu64 "\n", tasan32, tavu, suuri);
    // @loppu stdint

    // @alku kierto
    uint8_t laskuri = 255;
    laskuri = laskuri + 1;   // etumerkitön: lasketaan modulo 256
    printf("255 + 1 = %d (uint8_t)\n", laskuri);
    // @loppu kierto

    // @alku jako
    printf("7 / 2 = %d, 7 %% 2 = %d\n", 7 / 2, 7 % 2);
    printf("-7 / 2 = %d, -7 %% 2 = %d\n", -7 / 2, -7 % 2);
    printf("7 / 2.0 = %g\n", 7 / 2.0);
    // @loppu jako

    // @alku literaalit
    int binaari = 0b1010'1010;   // C23: binääriliteraali
    int heksa = 0xFF;
    int oktaali = 017;           // etunolla tarkoittaa oktaalia!
    printf("%d %d %d\n", binaari, heksa, oktaali);
    // @loppu literaalit
}
