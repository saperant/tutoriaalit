// Ohjelma, joka käyttää apukirjastoa. Riisuttu versio on analyysin
// kohde, symbolillinen versio vain tulosten tarkistamiseen.
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

uint32_t crc32_paivita(uint32_t crc, const uint8_t *data, size_t n);
char *kopioi(const char *s);
void heksaksi(char *kohde, const uint8_t *data, size_t n);

static void tulosta_tarkiste(const char *viesti)
{
    uint8_t tavut[4];
    char heksa[9];
    uint32_t crc = crc32_paivita(0, (const uint8_t *)viesti,
                                 strlen(viesti));
    for (int i = 0; i < 4; i++) {
        tavut[i] = (uint8_t)(crc >> (24 - 8 * i));
    }
    heksaksi(heksa, tavut, sizeof tavut);
    printf("%s: %s\n", viesti, heksa);
}

int main(int argc, char **argv)
{
    char *viesti = kopioi(argc > 1 ? argv[1] : "takaisinmallinnus");
    if (viesti == NULL) {
        return 1;
    }
    tulosta_tarkiste(viesti);
    free(viesti);
    return 0;
}
