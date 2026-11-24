// Kertolaskujen kertymä: montako bittiä summa tarvitsee?
#include <stdint.h>
#include <stdio.h>

int main(void)
{
    // @alku kertyma
    // 64 tuloa 0,9 * 0,9 kertyy Q2.30-tuloista. Kertymä pidetään
    // 64-bittisenä (kuten 40-bittinen DSP-kertymä), ja tarkistetaan,
    // mahtuisiko se 32 bittiin.
    const int16_t a = 29491;                  // 0,9 Q1.15:nä
    int64_t kertyma = 0;
    int ylitys = -1;
    for (int i = 0; i < 64; i++) {
        kertyma += (int32_t)a * a;            // Q2.30, noin 0,81
        if (ylitys < 0 && kertyma > INT32_MAX) {
            ylitys = i + 1;
        }
    }
    printf("summa %.4f, Q2.30-koodina %lld\n",
           (double)kertyma / (1 << 30), (long long)kertyma);
    printf("32-bittinen kertymä ylittyy %d. tulon kohdalla\n", ylitys);
    printf("40 bittiä: 8 vartijabittiä riittää %d tuloon\n", 1 << 8);
    // @loppu kertyma
    return 0;
}
