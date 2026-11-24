/* I2C-rajapinnan yhteiset apufunktiot. */
#include "i2c.h"

const char *i2c_tila_nimi(i2c_tila_t tila) {
    switch (tila) {
    case I2C_OK: return "ok";
    case I2C_NACK_OSOITE: return "osoitetta ei kuitattu";
    case I2C_NACK_DATA: return "tavua ei kuitattu";
    case I2C_JUMISSA: return "vayla jumissa";
    case I2C_AIKARAJA: return "aikaraja";
    }
    return "?";
}
