// Stokastinen pyöristys kokonaisluvuilla: satunnaisbitit lisätään ennen
// katkaisua. Satunnaisuus tulee LFSR:stä, kuten laitteistossa.
#include <stdint.h>
#include <stdio.h>

// @alku lfsr
// 16-bittinen siirtorekisteri takaisinkytkennällä
// (x^16 + x^14 + x^13 + x^11 + 1): käy läpi kaikki 65535 nollasta
// poikkeavaa tilaa ennen kuin toistuu.
static uint16_t lfsr(uint16_t s)
{
    unsigned bitti = (s ^ (s >> 2) ^ (s >> 3) ^ (s >> 5)) & 1u;
    return (uint16_t)((s >> 1) | (bitti << 15));
}
// @loppu lfsr

// @alku pudotus
// Pudottaa arvosta k alinta bittiä. Katkaisu hylkää ne, lähimpään
// pyöristys lisää ensin puolikkaan ja stokastinen satunnaisluvun r,
// 0 <= r < 2^k: ylöspäin pyöristyy osuus (x mod 2^k) / 2^k kerroista.
static uint32_t katkaisu(uint32_t x, unsigned k)
{
    return x >> k;
}

static uint32_t lahimpaan(uint32_t x, unsigned k)
{
    return (x + (1u << (k - 1))) >> k;
}

static uint32_t stokastinen(uint32_t x, unsigned k, uint16_t satunnainen)
{
    uint32_t r = satunnainen & ((1u << k) - 1u);
    return (x + r) >> k;
}
// @loppu pudotus

int main(void)
{
    // 12-bittinen näyte 8 bittiin: neljä alinta bittiä pois.
    const uint32_t nayte = 0x123;          // 291 = 18,1875 * 16
    const unsigned k = 4;
    uint64_t summa = 0;
    uint32_t jakso = 0;
    uint16_t s = 0xace1;
    do {                                   // koko LFSR:n jakso
        summa += stokastinen(nayte, k, s);
        s = lfsr(s);
        jakso++;
    } while (s != 0xace1);
    printf("jakso %u\n", (unsigned)jakso);
    printf("tarkka       %.4f\n", (double)nayte / 16.0);
    printf("katkaisu     %u\n", (unsigned)katkaisu(nayte, k));
    printf("lähimpään    %u\n", (unsigned)lahimpaan(nayte, k));
    printf("stokastinen  %.4f (keskiarvo jakson yli)\n",
           (double)summa / (double)jakso);
    return 0;
}
