// Kahden komplementti: sama bittikuvio, kaksi tulkintaa.
#include <stdint.h>
#include <stdio.h>

static void bitit8(uint8_t x, char *ulos)
{
    for (int i = 7; i >= 0; i--) {
        *ulos++ = (x >> i) & 1u ? '1' : '0';
    }
    *ulos = '\0';
}

int main(void)
{
    // @alku tulkinnat
    const int8_t arvot[] = {0, 1, 2, 127, -128, -2, -1};
    printf("int8_t  bitit     uint8_t\n");
    for (size_t i = 0; i < sizeof arvot; i++) {
        char b[9];
        uint8_t kuvio = (uint8_t)arvot[i];   // määritelty: modulo 256
        bitit8(kuvio, b);
        printf("%6d  %s  %7u\n", arvot[i], b, kuvio);
    }
    // @loppu tulkinnat

    // @alku vastaluku
    // Vastaluku: käännä bitit ja lisää yksi (~x + 1).
    uint8_t viisi = 5;
    uint8_t vasta = (uint8_t)(~viisi + 1u);
    printf("~5 + 1 = %u = %d\n", vasta, (int8_t)vasta);
    // @loppu vastaluku
    return 0;
}
