/* I2C-väylä ohjelmallisesti: väylän skannaus ja TMP105-anturin
 * rekisterit. QEMU kytkee väylään anturin (0x48) ja EEPROMin
 * (0x50), ks. Makefile. */
#include <stddef.h>
#include <stdint.h>

#include "i2c_sbcon.h"
#include "konsoli.h"
#include "mps2.h"

// @alku tmp105
/* TMP105: osoitinrekisteri valitsee, mihin rekisteriin seuraava
 * luku tai kirjoitus kohdistuu. */
enum {
    TMP105_OSOITE = 0x48,
    TMP105_LAMPO = 0, /* 16 bittiä, vain luku */
    TMP105_ASETUS = 1, /* 8 bittiä */
    TMP105_ALARAJA = 2, /* 16 bittiä */
    TMP105_YLARAJA = 3, /* 16 bittiä */
};

/* Rekisterin luku: osoittimen kirjoitus, toistettu START, luku. */
static i2c_tila_t lue_rekisteri(i2c_vayla_t *v, uint8_t rekisteri,
                                uint8_t *data, size_t n) {
    return i2c_siirto(v, TMP105_OSOITE, &rekisteri, 1, data, n);
}

static i2c_tila_t kirjoita_raja(i2c_vayla_t *v, uint8_t rekisteri,
                                int16_t arvo) {
    const uint8_t data[3] = {rekisteri, (uint8_t)((uint16_t)arvo >> 8),
                             (uint8_t)arvo};
    return i2c_siirto(v, TMP105_OSOITE, data, sizeof data, NULL, 0);
}

/* Lämpötilarekisterit ovat 1/256 asteen yksiköissä (ylin tavu on
 * kokonaiset asteet). Tulostetaan kymmenesosina. */
static void tulosta_lampo(const char *nimi, const uint8_t raaka[2]) {
    int16_t arvo = (int16_t)(raaka[0] << 8 | raaka[1]);
    int kymmenykset = arvo * 10 / 256;
    tulosta("%s %02x%02x = %d.%d C\n", nimi, raaka[0], raaka[1],
            kymmenykset / 10, kymmenykset % 10);
}
// @loppu tmp105

// @alku skannaus
static void skannaa(i2c_vayla_t *v) {
    tulosta("skannaus 0x08..0x77:");
    for (uint8_t osoite = 0x08; osoite < 0x78; osoite++) {
        if (i2c_siirto(v, osoite, NULL, 0, NULL, 0) == I2C_OK) {
            tulosta(" %02x", osoite);
        }
    }
    tulosta("\n");
}
// @loppu skannaus

// @alku main
int main(void) {
    konsoli_alusta();
    static i2c_sbcon_t ohjain;
    i2c_tila_t tila = i2c_sbcon_alusta(&ohjain, I2C_ANTURIT);
    tulosta("alustus: %s\n", i2c_tila_nimi(tila));
    i2c_vayla_t *v = &ohjain.vayla;
    skannaa(v);

    uint8_t asetus;
    uint8_t raja[2];
    tila = lue_rekisteri(v, TMP105_ASETUS, &asetus, 1);
    tulosta("asetus %02x (%s)\n", asetus, i2c_tila_nimi(tila));
    (void)lue_rekisteri(v, TMP105_ALARAJA, raja, 2);
    tulosta_lampo("alaraja", raja);
    (void)lue_rekisteri(v, TMP105_YLARAJA, raja, 2);
    tulosta_lampo("ylaraja", raja);

    tila = kirjoita_raja(v, TMP105_YLARAJA, 85 * 256 + 128);
    tulosta("ylaraja := 85.5 C (%s)\n", i2c_tila_nimi(tila));
    (void)lue_rekisteri(v, TMP105_YLARAJA, raja, 2);
    tulosta_lampo("ylaraja", raja);

    /* Väärä osoite: kukaan ei kuittaa. */
    uint8_t roska;
    tila = i2c_siirto(v, 0x49, NULL, 0, &roska, 1);
    tulosta("luku osoitteesta 49: %s\n", i2c_tila_nimi(tila));
    return 0;
}
// @loppu main
