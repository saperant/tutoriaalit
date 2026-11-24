// Ohjaimen ja laitteen välinen sarjaliikenne, joka tallennetaan
// kaappaustiedostoon. Protokolla on dokumentoimaton; analyysi päättelee
// sen kaappauksesta. Tämä lähdekoodi on vain tulosten tarkistamista
// varten.
#include <stdint.h>
#include <stdio.h>
#include <string.h>

enum { TAHDISTUS = 0xA5 };

static FILE *kaappaus;

// Kaappaustietue: suunta (0 ohjain->laite, 1 laite->ohjain),
// pituus (u16 LE) ja kehyksen tavut.
static void tallenna(int suunta, const uint8_t *kehys, size_t n)
{
    uint8_t otsake[3] = {(uint8_t)suunta, (uint8_t)n, (uint8_t)(n >> 8)};
    fwrite(otsake, 1, sizeof otsake, kaappaus);
    fwrite(kehys, 1, n, kaappaus);
}

static size_t kehysta(uint8_t *kehys, uint8_t tyyppi, uint8_t numero,
                      const uint8_t *data, uint8_t n)
{
    kehys[0] = TAHDISTUS;
    kehys[1] = tyyppi;
    kehys[2] = numero;
    kehys[3] = n;
    memcpy(kehys + 4, data, n);
    uint8_t summa = 0;
    for (size_t i = 1; i < 4u + n; i++) {
        summa = (uint8_t)(summa + kehys[i]);
    }
    kehys[4 + n] = summa;
    return 5u + n;
}

// Laite: vastaa pyyntöön tyypillä pyyntö | 0x80 ja samalla numerolla.
static size_t laite(const uint8_t *pyynto, uint8_t *vastaus)
{
    static uint16_t asetukset[4] = {100, 200, 300, 400};
    static int16_t lampo = 2310;
    uint8_t data[16];
    uint8_t n = 0;
    switch (pyynto[1]) {
    case 0x01: // tila: lämpötila (i16 LE) ja tila
        data[0] = (uint8_t)lampo;
        data[1] = (uint8_t)((uint16_t)lampo >> 8);
        data[2] = 0x01;
        n = 3;
        lampo = (int16_t)(lampo + 15);
        break;
    case 0x02: // aseta: kanava ja arvo (u16 LE); vastaus: tila, vanha arvo
        if (pyynto[4] < 4) {
            uint16_t vanha = asetukset[pyynto[4]];
            asetukset[pyynto[4]] = (uint16_t)(pyynto[5] | pyynto[6] << 8);
            data[0] = 0x00;
            data[1] = (uint8_t)vanha;
            data[2] = (uint8_t)(vanha >> 8);
            n = 3;
        } else {
            data[0] = 0x02; // virheellinen kanava
            n = 1;
        }
        break;
    case 0x03: // nimi
        memcpy(data, "TK-7 v1.4", 9);
        n = 9;
        break;
    }
    return kehysta(vastaus, (uint8_t)(pyynto[1] | 0x80), pyynto[2], data, n);
}

int main(void)
{
    kaappaus = fopen("kaappaus.bin", "wb");
    if (kaappaus == NULL) {
        return 1;
    }
    const struct {
        uint8_t tyyppi;
        uint8_t n;
        uint8_t data[3];
    } pyynnot[] = {
        {0x03, 0, {0}},          {0x01, 0, {0}},
        {0x02, 3, {1, 0xE8, 0x03}}, {0x01, 0, {0}},
        {0x02, 3, {7, 0x10, 0x00}}, {0x01, 0, {0}},
    };
    uint8_t numero = 0x40;
    for (size_t i = 0; i < sizeof pyynnot / sizeof pyynnot[0]; i++) {
        uint8_t kehys[32], vastaus[32];
        size_t n = kehysta(kehys, pyynnot[i].tyyppi, numero++,
                           pyynnot[i].data, pyynnot[i].n);
        tallenna(0, kehys, n);
        tallenna(1, vastaus, laite(kehys, vastaus));
    }
    return fclose(kaappaus) == 0 ? 0 : 1;
}
