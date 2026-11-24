/* I2C-väylän ajurirajapinta. Laiteajurit (esim. at24.h) käyttävät
 * väylää vain tämän rajapinnan kautta, joten sama laiteajuri toimii
 * millä tahansa väyläohjaimella ja isäntäkoneen testissä mallia
 * vastaan. */
#ifndef I2C_H
#define I2C_H

#include <stddef.h>
#include <stdint.h>

// @alku rajapinta
typedef enum {
    I2C_OK = 0,
    I2C_NACK_OSOITE, /* kukaan ei kuitannut osoitetta */
    I2C_NACK_DATA,   /* laite hylkäsi kirjoitetun tavun */
    I2C_JUMISSA,     /* SDA alhaalla, väylää ei saatu vapaaksi */
    I2C_AIKARAJA,    /* laite piti SCL:n alhaalla liian kauan */
} i2c_tila_t;

typedef struct i2c_vayla i2c_vayla_t;

struct i2c_vayla {
    /* Yksi siirto: START, kirjoitus_n tavua laitteelle, toistettu
     * START ja luku_n tavua laitteelta, STOP. Kumpi tahansa osa voi
     * olla tyhjä; jos molemmat ovat, siirto vain kysyy osoitetta. */
    i2c_tila_t (*siirto)(i2c_vayla_t *vayla, uint8_t osoite,
                         const uint8_t *kirjoitus, size_t kirjoitus_n,
                         uint8_t *luku, size_t luku_n);
};

static inline i2c_tila_t i2c_siirto(i2c_vayla_t *vayla, uint8_t osoite,
                                    const uint8_t *kirjoitus,
                                    size_t kirjoitus_n, uint8_t *luku,
                                    size_t luku_n) {
    return vayla->siirto(vayla, osoite, kirjoitus, kirjoitus_n, luku,
                         luku_n);
}
// @loppu rajapinta

const char *i2c_tila_nimi(i2c_tila_t tila);

#endif
