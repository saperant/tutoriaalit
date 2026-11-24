/* AT24-sarjan I2C-EEPROM (esim. 24C02: 256 tavua, 8 tavun sivut).
 * Ajuri ei tunne väyläohjainta: se saa i2c_vayla_t-osoittimen. */
#ifndef AT24_H
#define AT24_H

#include <stddef.h>
#include <stdint.h>

#include "i2c.h"

// @alku rajapinta
typedef enum {
    AT24_OK = 0,
    AT24_ALUE,     /* osoite tai pituus muistin ulkopuolella */
    AT24_EI_VASTAA, /* laite ei kuittaa osoitettaan */
    AT24_VAYLA,    /* muu väylävirhe */
    AT24_KIIRE,    /* kirjoitus ei valmistunut kyselyrajan aikana */
} at24_tila_t;

typedef struct {
    i2c_vayla_t *vayla;
    uint8_t osoite;    /* 0x50..0x57 osoitenastojen mukaan */
    uint16_t koko;     /* tavuja, enintään 256 (yksitavuinen osoite) */
    uint8_t sivu;      /* sivun koko tavuina, kahden potenssi */
    unsigned kyselyt;  /* ACK-kyselyjä kirjoituksen jälkeen */
} at24_t;

at24_tila_t at24_lue(const at24_t *e, uint16_t osoite, uint8_t *kohde,
                     size_t n);
at24_tila_t at24_kirjoita(const at24_t *e, uint16_t osoite,
                          const uint8_t *data, size_t n);
const char *at24_tila_nimi(at24_tila_t tila);
// @loppu rajapinta

#endif
