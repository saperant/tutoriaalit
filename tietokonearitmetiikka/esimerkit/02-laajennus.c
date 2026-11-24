// Kiihtyvyysanturi palauttaa 12-bittisen kahden komplementin arvon
// 16-bittisessä rekisterissä. Etumerkki on laajennettava itse.
#include <stdint.h>
#include <stdio.h>

// @alku laajennus
// Tulkitsee n alinta bittiä kahden komplementin lukuna.
static int32_t laajenna(uint32_t raaka, unsigned n)
{
    uint32_t maski = (1u << n) - 1u;
    uint32_t arvo = raaka & maski;
    uint32_t merkki = 1u << (n - 1);
    // Siirretään väli [-2^(n-1), 2^(n-1)) nollan ympärille.
    return (int32_t)(arvo ^ merkki) - (int32_t)merkki;
}
// @loppu laajennus

int main(void)
{
    const uint16_t rekisterit[] = {0x0000, 0x0001, 0x07ff, 0x0800,
                                   0x0fff, 0xf123};
    const double mg_per_lsb = 3.9;   // datalehden herkkyys
    for (size_t i = 0; i < 6; i++) {
        int32_t lsb = laajenna(rekisterit[i], 12);
        printf("0x%04x -> %5d -> %8.1f mg\n", rekisterit[i], lsb,
               lsb * mg_per_lsb);
    }
    return 0;
}
