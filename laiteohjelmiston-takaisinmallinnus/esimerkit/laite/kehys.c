/* Huoltotyökalun lähettämien kehysten käsittely. */
#include <string.h>

#include "kehys.h"
#include "loki.h"
#include "mps2.h"
#include "tarkiste.h"

static char nimi_ram[16] = "LT-100";
static uint32_t kello_ms;

const char *laitteen_nimi(void) {
    return nimi_ram;
}

uint32_t kellonaika(void) {
    return kello_ms;
}

int kasittele_kehys(const uint8_t *kehys, size_t n) {
    if (n < 4 || n != (size_t)kehys[1] + 4) {
        return KEHYS_LYHYT;
    }
    size_t pituus = kehys[1];
    uint16_t crc = (uint16_t)(kehys[2 + pituus] << 8 | kehys[3 + pituus]);
    if (crc16_ccitt(kehys, 2 + pituus) != crc) {
        return KEHYS_TARKISTE;
    }
    const uint8_t *data = &kehys[2];
    switch (kehys[0]) {
    case KEHYS_KELLO:
        if (pituus != 4) {
            return KEHYS_LYHYT;
        }
        kello_ms = (uint32_t)data[0] | (uint32_t)data[1] << 8 |
                   (uint32_t)data[2] << 16 | (uint32_t)data[3] << 24;
        return KEHYS_OK;
    case KEHYS_NIMI: {
        char nimi[16];
#ifdef KORJATTU
        if (pituus >= sizeof nimi) {
            return KEHYS_LIIAN_PITKA;
        }
#endif
        memcpy(nimi, data, pituus); /* VIRHE ilman KORJATTU-tarkistusta */
        nimi[pituus] = '\0';
        size_t i = 0;
        for (; i + 1 < sizeof nimi_ram && nimi[i] != '\0'; i++) {
            nimi_ram[i] = nimi[i];
        }
        nimi_ram[i] = '\0';
        return KEHYS_OK;
    }
    case KEHYS_LED:
        if (pituus != 1) {
            return KEHYS_LYHYT;
        }
        FPGAIO_LED = data[0] & 3u;
        return KEHYS_OK;
    case KEHYS_NOLLAA:
        loki_nollaa();
        return KEHYS_OK;
    case KEHYS_KAIKU:
        laheta_kehys(KEHYS_KAIKU, data, pituus);
        return KEHYS_OK;
    default:
        return KEHYS_TUNTEMATON;
    }
}
