// Mittalaitteen tallennusohjelma, jonka tiedostomuoto on
// dokumentoimaton. Analyysi selvittää muodon tiedostosta itsestään;
// tätä lähdekoodia käytetään vain tulosten tarkistamiseen.
#include <stdint.h>
#include <stdio.h>
#include <string.h>

struct mittaus {
    uint32_t aika;
    int16_t lampotila; // sadasosa-asteina
    uint16_t kosteus;  // promilleina
    uint8_t anturi;
    const char *nimi;
};

static uint32_t crc;

static void kirjoita(FILE *f, const void *data, size_t n)
{
    const uint8_t *p = data;
    for (size_t i = 0; i < n; i++) {
        crc ^= p[i];
        for (int b = 0; b < 8; b++) {
            crc = (crc >> 1) ^ (0xEDB88320u & (0u - (crc & 1u)));
        }
    }
    fwrite(data, 1, n, f);
}

static void le16(FILE *f, uint16_t x)
{
    uint8_t t[2] = {(uint8_t)x, (uint8_t)(x >> 8)};
    kirjoita(f, t, 2);
}

static void le32(FILE *f, uint32_t x)
{
    uint8_t t[4] = {(uint8_t)x, (uint8_t)(x >> 8), (uint8_t)(x >> 16),
                    (uint8_t)(x >> 24)};
    kirjoita(f, t, 4);
}

int main(void)
{
    const struct mittaus mittaukset[] = {
        {1767225600, 2150, 412, 1, "olohuone"},
        {1767225900, 2135, 418, 1, "olohuone"},
        {1767226200, -480, 873, 2, "parveke"},
        {1767226500, 655, 701, 3, "kellari"},
    };
    const uint32_t n = sizeof mittaukset / sizeof mittaukset[0];
    FILE *f = fopen("mittaukset.kmt", "wb");
    if (f == NULL) {
        return 1;
    }
    crc = 0xFFFFFFFFu;
    kirjoita(f, "KMTD", 4);
    le16(f, 2);      // versio
    le16(f, 0x0001); // liput: kalibrointilohko mukana
    le32(f, n);
    for (uint32_t i = 0; i < n; i++) {
        const struct mittaus *m = &mittaukset[i];
        le32(f, m->aika);
        le16(f, (uint16_t)m->lampotila);
        le16(f, m->kosteus);
        uint8_t anturi_ja_pituus[2] = {m->anturi, (uint8_t)strlen(m->nimi)};
        kirjoita(f, anturi_ja_pituus, 2);
        kirjoita(f, m->nimi, strlen(m->nimi));
    }
    // Salattu kalibrointilohko: näennäisesti satunnaista dataa.
    uint8_t lohko[192];
    uint32_t tila = 0x2026u;
    for (size_t i = 0; i < sizeof lohko; i++) {
        tila ^= tila << 13;
        tila ^= tila >> 17;
        tila ^= tila << 5;
        lohko[i] = (uint8_t)(tila >> 24);
    }
    le32(f, sizeof lohko);
    kirjoita(f, lohko, sizeof lohko);
    uint32_t tarkiste = ~crc;
    le32(f, tarkiste);
    return fclose(f) == 0 ? 0 : 1;
}
