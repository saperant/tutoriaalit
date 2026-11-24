// IPv4-otsakkeen ensimmäisen sanan kentät bittioperaatioilla.
#include <stdint.h>
#include <stdio.h>

// @alku kentta
// Palauttaa kentän, joka alkaa bitistä alku (0 = vähiten merkitsevä)
// ja on leveys bittiä leveä.
static uint32_t kentta(uint32_t sana, unsigned alku, unsigned leveys)
{
    return (sana >> alku) & ((1u << leveys) - 1u);
}
// @loppu kentta

int main(void)
{
    // Verkosta luetut tavut ovat suurimman tavun järjestyksessä.
    const uint8_t tavut[4] = {0x45, 0xb8, 0x05, 0xdc};
    // @alku tavut
    uint32_t sana = (uint32_t)tavut[0] << 24 | (uint32_t)tavut[1] << 16 |
                    (uint32_t)tavut[2] << 8 | tavut[3];
    printf("versio %u, otsakkeen pituus %u tavua\n", kentta(sana, 28, 4),
           kentta(sana, 24, 4) * 4);
    printf("DSCP %u, ECN %u, kokonaispituus %u\n", kentta(sana, 18, 6),
           kentta(sana, 16, 2), kentta(sana, 0, 16));
    // @loppu tavut
    return 0;
}
