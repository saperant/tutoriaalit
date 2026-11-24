// Kääntäjä korvaa jakolaskun vakiolla kertolaskulla ja siirrolla.
#include <stdint.h>
#include <stdio.h>

// @alku kymmenella
// x / 10 kaikille 32-bittisille x: kerroin on ceil(2^35 / 10).
static uint32_t jaa_kymmenella(uint32_t x)
{
    return (uint32_t)(((uint64_t)x * 0xCCCCCCCDu) >> 35);
}
// @loppu kymmenella

int main(void)
{
    uint64_t tarkistettu = 0;
    bool oikein = true;
    for (uint64_t x = 0; x <= UINT32_MAX; x += 9973) {
        oikein = oikein && jaa_kymmenella((uint32_t)x) == x / 10;
        tarkistettu++;
    }
    oikein = oikein && jaa_kymmenella(UINT32_MAX) == UINT32_MAX / 10;
    printf("%llu arvoa, kaikki oikein: %d\n",
           (unsigned long long)tarkistettu, oikein);
    // @alku siirrot
    int a = -7;
    printf("-7 / 2 = %d, -7 >> 1 = %d\n", a / 2, a >> 1);
    printf("x * 10 = (x << 3) + (x << 1): %d\n", (13 << 3) + (13 << 1));
    // @loppu siirrot
    return 0;
}
