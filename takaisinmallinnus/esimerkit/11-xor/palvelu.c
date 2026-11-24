// Ohjelma, joka piilottaa merkkijononsa XOR-salauksella.
#include <stddef.h>
#include <stdio.h>

#include "salaisuudet.h"

// @alku pura
// Purkaa XOR-salatun jonon puskuriin; avain k[i] = 0x5c + 0x1d * i.
[[gnu::noinline]] static const char *
pura(const unsigned char *salattu, size_t n, char *puskuri)
{
    unsigned char avain = 0x5c;
    for (size_t i = 0; i < n; i++) {
        puskuri[i] = (char)(salattu[i] ^ avain);
        avain = (unsigned char)(avain + 0x1d);
    }
    return puskuri;
}
// @loppu pura

int main(void)
{
    char palvelin[64], polku[64], otsake[64];
    printf("yhdistetään: %s\n", pura(PALVELIN, sizeof PALVELIN, palvelin));
    printf("pyyntö: POST %s\n", pura(POLKU, sizeof POLKU, polku));
    printf("otsake: %s\n", pura(OTSAKE, sizeof OTSAKE, otsake));
    return 0;
}
