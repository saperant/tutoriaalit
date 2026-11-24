// Rekisterin leveys ja tavujärjestys: sama C-rajapinta, kaksi
// toteutusta.
#include <stdint.h>
#include <stdio.h>

long lisaa32(long a, long b);
unsigned tavu(const uint32_t *p, long i);

int main(void) {
    // 2 000 000 000 + 2 000 000 000 ei mahdu 32-bittiseen int-tyyppiin.
    printf("lisaa32: %ld\n", lisaa32(2000000000, 2000000000));
    uint32_t sana = 0x11223344;
    printf("tavut muistissa:");
    for (long i = 0; i < 4; i++) {
        printf(" %02x", tavu(&sana, i));
    }
    printf("\n");
    return 0;
}
