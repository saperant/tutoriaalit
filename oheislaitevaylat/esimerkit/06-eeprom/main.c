/* EEPROM-ajuri kohdelaitteessa: sama at24.c, joka testataan
 * isäntäkoneella mallia vastaan (isanta/at24_testi.c), käyttää tässä
 * SBCon-väyläohjainta. */
#include <stddef.h>
#include <stdint.h>

#include "at24.h"
#include "i2c_sbcon.h"
#include "konsoli.h"
#include "mps2.h"

static void vedos(const at24_t *e, uint16_t alku, size_t n) {
    uint8_t data[16];
    at24_tila_t tila = at24_lue(e, alku, data, n);
    if (tila != AT24_OK) {
        tulosta("luku %02x: %s\n", alku, at24_tila_nimi(tila));
        return;
    }
    tulosta("%02x:", alku);
    for (size_t i = 0; i < n; i++) {
        tulosta(" %02x", data[i]);
    }
    tulosta("\n");
}

// @alku main
int main(void) {
    konsoli_alusta();
    static i2c_sbcon_t ohjain;
    if (i2c_sbcon_alusta(&ohjain, I2C_ANTURIT) != I2C_OK) {
        tulosta("vayla ei vapaudu\n");
        return 1;
    }
    /* 24C02: 256 tavua ja 8 tavun sivut osoitteessa 0x50. */
    const at24_t eeprom = {&ohjain.vayla, 0x50, 256, 8, 100};

    static const char nimi[] = "laite-0042";
    at24_tila_t tila = at24_kirjoita(&eeprom, 0x05, (const uint8_t *)nimi,
                                     sizeof nimi - 1);
    tulosta("kirjoitus 05..0e: %s\n", at24_tila_nimi(tila));
    vedos(&eeprom, 0x00, 16);

    uint8_t luettu[sizeof nimi] = {0};
    tila = at24_lue(&eeprom, 0x05, luettu, sizeof nimi - 1);
    tulosta("luku: %s \"%s\"\n", at24_tila_nimi(tila), (char *)luettu);

    /* Virheet: alueen ylitys ja puuttuva laite. */
    tila = at24_lue(&eeprom, 0xF8, luettu, 9);
    tulosta("luku f8..100: %s\n", at24_tila_nimi(tila));
    const at24_t puuttuva = {&ohjain.vayla, 0x51, 256, 8, 100};
    tila = at24_kirjoita(&puuttuva, 0, luettu, 1);
    tulosta("kirjoitus osoitteeseen 51: %s\n", at24_tila_nimi(tila));
    return 0;
}
// @loppu main
