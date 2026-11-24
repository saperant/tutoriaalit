// Etumerkittömät laskurit kiertävät: 16-bittiset järjestysnumerot.
#include <stdint.h>
#include <stdio.h>

// @alku jarjestys
// Onko paketti a uudempi kuin b, kun numerot kiertävät 65535 -> 0?
// Erotus lasketaan modulo 2^16 ja tulkitaan etumerkillisenä.
static bool uudempi(uint16_t a, uint16_t b)
{
    return (int16_t)(uint16_t)(a - b) > 0;
}
// @loppu jarjestys

int main(void)
{
    // @alku kierto
    uint16_t numero = 65534;
    for (int i = 0; i < 4; i++) {
        printf("%u ", numero);
        numero++;                 // määritelty: modulo 65536
    }
    printf("\n");
    // @loppu kierto
    printf("%d %d %d\n", uudempi(5, 3), uudempi(2, 65530),
           uudempi(65530, 2));
    uint32_t edellinen = 4294967000u;   // aikaleima ennen kiertoa
    uint32_t nyt = 704u;                // ja sen jälkeen
    printf("kulunut %u ms\n", nyt - edellinen);
    return 0;
}
