// Pieni apukirjasto, joka linkitetään ohjelmaan staattisesti. Sen
// funktioista tehdään allekirjoitukset, joilla ne tunnistetaan
// riisutusta ohjelmasta.
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

uint32_t crc32_paivita(uint32_t crc, const uint8_t *data, size_t n)
{
    crc = ~crc;
    for (size_t i = 0; i < n; i++) {
        crc ^= data[i];
        for (int b = 0; b < 8; b++) {
            crc = (crc >> 1) ^ (0xEDB88320u & (0u - (crc & 1u)));
        }
    }
    return ~crc;
}

// Kopioi merkkijonon uuteen varattuun puskuriin; NULL, jos muisti loppuu.
char *kopioi(const char *s)
{
    size_t n = strlen(s) + 1;
    char *uusi = malloc(n);
    if (uusi != NULL) {
        memcpy(uusi, s, n);
    }
    return uusi;
}

static const char HEKSA[] = "0123456789abcdef";

// Kirjoittaa n tavua heksadesimaalina puskuriin (2n + 1 merkkiä).
void heksaksi(char *kohde, const uint8_t *data, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        kohde[2 * i] = HEKSA[data[i] >> 4];
        kohde[2 * i + 1] = HEKSA[data[i] & 0xF];
    }
    kohde[2 * n] = '\0';
}
