/* AT24-EEPROM-ajuri. */
#include "at24.h"

#include <string.h>

const char *at24_tila_nimi(at24_tila_t tila) {
    switch (tila) {
    case AT24_OK: return "ok";
    case AT24_ALUE: return "alueen ulkopuolella";
    case AT24_EI_VASTAA: return "ei vastaa";
    case AT24_VAYLA: return "vaylavirhe";
    case AT24_KIIRE: return "kirjoitus ei valmistu";
    }
    return "?";
}

// @alku virheet
/* Väylän virhe käännetään laitteen kielelle: kutsuja ei tiedä,
 * kumpi NACK on kumpi, mutta tietää, vastaako laite ylipäätään. */
static at24_tila_t muunna(i2c_tila_t tila) {
    switch (tila) {
    case I2C_OK: return AT24_OK;
    case I2C_NACK_OSOITE: return AT24_EI_VASTAA;
    default: return AT24_VAYLA;
    }
}
// @loppu virheet

static int alueella(const at24_t *e, uint16_t osoite, size_t n) {
    return osoite <= e->koko && n <= (size_t)(e->koko - osoite);
}

// @alku lue
at24_tila_t at24_lue(const at24_t *e, uint16_t osoite, uint8_t *kohde,
                     size_t n) {
    if (!alueella(e, osoite, n)) {
        return AT24_ALUE;
    }
    if (n == 0) {
        return AT24_OK;
    }
    /* Osoitteen kirjoitus, toistettu START ja peräkkäisluku: piiri
     * kasvattaa sisäistä osoitettaan jokaisen tavun jälkeen. */
    uint8_t osoitetavu = (uint8_t)osoite;
    return muunna(i2c_siirto(e->vayla, e->osoite, &osoitetavu, 1,
                             kohde, n));
}
// @loppu lue

// @alku odota
/* Sisäisen kirjoitusjakson (tyypillisesti enintään 5 ms) ajan piiri
 * ei kuittaa osoitettaan. Kysytään, kunnes se vastaa. */
static at24_tila_t odota_valmis(const at24_t *e) {
    for (unsigned kysely = 0; kysely < e->kyselyt; kysely++) {
        i2c_tila_t tila = i2c_siirto(e->vayla, e->osoite, NULL, 0,
                                     NULL, 0);
        if (tila == I2C_OK) {
            return AT24_OK;
        }
        if (tila != I2C_NACK_OSOITE) {
            return muunna(tila);
        }
    }
    return AT24_KIIRE;
}
// @loppu odota

// @alku kirjoita
at24_tila_t at24_kirjoita(const at24_t *e, uint16_t osoite,
                          const uint8_t *data, size_t n) {
    if (!alueella(e, osoite, n)) {
        return AT24_ALUE;
    }
    while (n > 0) {
        /* Yksi kirjoitus saa ulottua vain sivun loppuun: piiri
         * kasvattaa vain osoitteen alimpia bittejä, joten yli menevät
         * tavut kiertäisivät sivun alkuun. */
        size_t sivulla = e->sivu - (osoite & (e->sivu - 1u));
#ifdef SIVUVIRHE
        sivulla = n; /* virheellinen: sivun rajaa ei huomioida */
#endif
        size_t osa = n < sivulla ? n : sivulla;
        uint8_t puskuri[1 + 64];
        if (osa > sizeof puskuri - 1) {
            osa = sizeof puskuri - 1;
        }
        puskuri[0] = (uint8_t)osoite;
        memcpy(&puskuri[1], data, osa);
        at24_tila_t tila = muunna(i2c_siirto(e->vayla, e->osoite,
                                             puskuri, 1 + osa, NULL, 0));
        if (tila == AT24_OK) {
            tila = odota_valmis(e);
        }
        if (tila != AT24_OK) {
            return tila;
        }
        osoite = (uint16_t)(osoite + osa);
        data += osa;
        n -= osa;
    }
    return AT24_OK;
}
// @loppu kirjoita
