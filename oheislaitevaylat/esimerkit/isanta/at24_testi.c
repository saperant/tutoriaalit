/* AT24-ajurin testi isäntäkoneella. Väylän tilalla on malli, joka
 * käyttäytyy kuten oikea piiri: osoite kiertää sivun sisällä, ja
 * kirjoituksen jälkeen piiri ei kuittaa osoitettaan hetkeen. QEMU:n
 * EEPROM-malli ei tee kumpaakaan, joten nämä virheet näkyvät vain
 * tässä. */
#include <stdio.h>
#include <string.h>

#include "at24.h"

// @alku malli
typedef struct {
    i2c_vayla_t vayla; /* ensimmäisenä, kuten oikeassa ohjaimessa */
    uint8_t osoite;
    uint8_t sivu;
    uint8_t muisti[256];
    uint8_t osoitin;
    unsigned kirjoitusaika; /* NACK-kyselyjä jokaisen kirjoituksen jälkeen */
    unsigned kiire;
    size_t hylkaa_tavu; /* > 0: n:s datatavu saa NACKin (vikasyöte) */
    unsigned siirtoja;
    unsigned kyselyja;
} malli_t;

static i2c_tila_t malli_siirto(i2c_vayla_t *vayla, uint8_t osoite,
                               const uint8_t *kirjoitus,
                               size_t kirjoitus_n, uint8_t *luku,
                               size_t luku_n) {
    malli_t *m = (malli_t *)vayla;
    m->siirtoja++;
    if (osoite != m->osoite) {
        return I2C_NACK_OSOITE;
    }
    if (m->kiire > 0) {
        m->kiire--;
        m->kyselyja++;
        return I2C_NACK_OSOITE;
    }
    if (kirjoitus_n > 0) {
        m->osoitin = kirjoitus[0];
    }
    const uint8_t maski = (uint8_t)(m->sivu - 1u);
    for (size_t i = 1; i < kirjoitus_n; i++) {
        if (i == m->hylkaa_tavu) {
            return I2C_NACK_DATA;
        }
        m->muisti[m->osoitin] = kirjoitus[i];
        /* Vain sivun sisäinen osa osoitteesta kasvaa. */
        m->osoitin = (uint8_t)((m->osoitin & ~maski) |
                               ((m->osoitin + 1u) & maski));
    }
    if (kirjoitus_n > 1) {
        m->kiire = m->kirjoitusaika;
    }
    for (size_t i = 0; i < luku_n; i++) {
        luku[i] = m->muisti[m->osoitin++];
    }
    return I2C_OK;
}

static void alusta(malli_t *m, unsigned kirjoitusaika) {
    memset(m, 0, sizeof *m);
    m->vayla.siirto = malli_siirto;
    m->osoite = 0x50;
    m->sivu = 8;
    memset(m->muisti, 0xFF, sizeof m->muisti);
    m->kirjoitusaika = kirjoitusaika;
}
// @loppu malli

static void vedos(const malli_t *m) {
    printf("  muisti 00..0f:");
    for (unsigned i = 0; i < 16; i++) {
        printf(" %02x", m->muisti[i]);
    }
    printf("\n");
}

// @alku testit
static int virheita;

static void odota(const char *nimi, at24_tila_t saatu, at24_tila_t odotettu) {
    printf("%-34s %s\n", nimi, at24_tila_nimi(saatu));
    if (saatu != odotettu) {
        printf("  VIRHE: odotettiin %s\n", at24_tila_nimi(odotettu));
        virheita++;
    }
}

int main(void) {
    malli_t m;
    static const char nimi[] = "laite-0042";
    const size_t n = sizeof nimi - 1;

    alusta(&m, 3);
    at24_t e = {&m.vayla, 0x50, 256, 8, 10};
    odota("kirjoitus 05..0e sivun yli", at24_kirjoita(&e, 0x05,
          (const uint8_t *)nimi, n), AT24_OK);
    printf("  siirtoja %u, joista kiirekyselyja %u\n", m.siirtoja,
           m.kyselyja);
    vedos(&m);
    char luettu[sizeof nimi] = {0};
    odota("luku 05..0e", at24_lue(&e, 0x05, (uint8_t *)luettu, n),
          AT24_OK);
    if (memcmp(luettu, nimi, n) != 0) {
        printf("  VIRHE: luettiin");
        for (size_t i = 0; i < n; i++) {
            printf(" %02x", (unsigned char)luettu[i]);
        }
        printf("\n");
        virheita++;
    }

    alusta(&m, 50); /* kirjoitusjakso pidempi kuin kyselyraja */
    odota("hidas piiri", at24_kirjoita(&e, 0, (const uint8_t *)"x", 1),
          AT24_KIIRE);
    alusta(&m, 0);
    m.hylkaa_tavu = 2;
    odota("piiri hylkaa toisen tavun", at24_kirjoita(&e, 0,
          (const uint8_t *)"xy", 2), AT24_VAYLA);
    odota("luku f8..ff", at24_lue(&e, 0xF8, (uint8_t *)luettu, 8),
          AT24_OK);
    odota("luku f8..100", at24_lue(&e, 0xF8, (uint8_t *)luettu, 9),
          AT24_ALUE);
    at24_t puuttuva = {&m.vayla, 0x51, 256, 8, 10};
    odota("puuttuva piiri", at24_lue(&puuttuva, 0, (uint8_t *)luettu, 1),
          AT24_EI_VASTAA);
    printf("%s\n", virheita ? "TESTIT EPAONNISTUIVAT" : "kaikki ok");
    return virheita != 0;
}
// @loppu testit
