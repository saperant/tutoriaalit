/* SBCon-pohjainen I2C-isäntä. Linjat ovat avokollektorilähtöjä:
 * kirjoitus CTRL-rekisteriin vapauttaa linjan, jolloin vetovastus
 * nostaa sen, ja kirjoitus CLR-rekisteriin vetää sen alas. */
#include "i2c_sbcon.h"

/* Kuinka monta kertaa SCL:n nousua odotetaan ennen kuin laitteen
 * kellonvenytys tulkitaan jumiksi. */
#define VENYTYS_RAJA 100000u

static void viive(const i2c_sbcon_t *o) {
    for (volatile unsigned i = 0; i < o->puolijakso; i++) {
    }
}

// @alku linjat
static void sda(const i2c_sbcon_t *o, unsigned taso) {
    if (taso) {
        o->linjat->CTRL = SBCON_SDA;
    } else {
        o->linjat->CLR = SBCON_SDA;
    }
}

static unsigned lue_sda(const i2c_sbcon_t *o) {
    return (o->linjat->CTRL & SBCON_SDA) != 0;
}

static void scl_alas(const i2c_sbcon_t *o) {
    o->linjat->CLR = SBCON_SCL;
    viive(o);
}

/* Vapauttaa SCL:n ja odottaa, että se todella nousee: laite saa
 * venyttää kellojaksoa pitämällä linjaa alhaalla. */
static int scl_ylos(const i2c_sbcon_t *o) {
    o->linjat->CTRL = SBCON_SCL;
    for (unsigned k = 0; !(o->linjat->CTRL & SBCON_SCL); k++) {
        if (k == VENYTYS_RAJA) {
            return 0;
        }
    }
    viive(o);
    return 1;
}
// @loppu linjat

// @alku ehdot
/* START: SDA laskee, kun SCL on ylhäällä. Toistettu START on sama
 * ehto ilman edeltävää STOPia. */
static int start(const i2c_sbcon_t *o) {
    sda(o, 1);
    if (!scl_ylos(o)) {
        return 0;
    }
    sda(o, 0);
    viive(o);
    scl_alas(o);
    return 1;
}

/* STOP: SDA nousee, kun SCL on ylhäällä. */
static void stop(const i2c_sbcon_t *o) {
    sda(o, 0);
    viive(o);
    (void)scl_ylos(o);
    sda(o, 1);
    viive(o);
}
// @loppu ehdot

// @alku tavut
/* Lähettää tavun eniten merkitsevä bitti ensin ja palauttaa
 * kuittauksen: 1 = ACK (laite veti SDA:n alas), 0 = NACK, -1 =
 * kellonvenytys ylitti rajan. */
static int laheta(const i2c_sbcon_t *o, uint8_t tavu) {
    for (int bitti = 7; bitti >= 0; bitti--) {
        sda(o, (tavu >> bitti) & 1u);
        if (!scl_ylos(o)) {
            return -1;
        }
        scl_alas(o);
    }
    sda(o, 1); /* vapautetaan SDA laitteen kuittausta varten */
    if (!scl_ylos(o)) {
        return -1;
    }
    int ack = !lue_sda(o);
    scl_alas(o);
    return ack;
}

/* Vastaanottaa tavun. Isäntä kuittaa (ACK) kaikki paitsi viimeisen
 * tavun; NACK kertoo laitteelle, että luku päättyy. */
static int vastaanota(const i2c_sbcon_t *o, int kuittaa, uint8_t *tavu) {
    uint8_t arvo = 0;
    sda(o, 1);
    for (int bitti = 0; bitti < 8; bitti++) {
        if (!scl_ylos(o)) {
            return 0;
        }
        arvo = (uint8_t)((arvo << 1) | lue_sda(o));
        scl_alas(o);
    }
    sda(o, kuittaa ? 0 : 1);
    if (!scl_ylos(o)) {
        return 0;
    }
    scl_alas(o);
    sda(o, 1);
    *tavu = arvo;
    return 1;
}
// @loppu tavut

// @alku siirto
static i2c_tila_t kuittaus(int ack, i2c_tila_t nack) {
    return ack > 0 ? I2C_OK : (ack == 0 ? nack : I2C_AIKARAJA);
}

static i2c_tila_t siirto(i2c_vayla_t *vayla, uint8_t osoite,
                         const uint8_t *kirjoitus, size_t kirjoitus_n,
                         uint8_t *luku, size_t luku_n) {
    const i2c_sbcon_t *o = (const i2c_sbcon_t *)vayla;
    i2c_tila_t tila = start(o) ? I2C_OK : I2C_AIKARAJA;
    if (tila == I2C_OK && (kirjoitus_n > 0 || luku_n == 0)) {
        tila = kuittaus(laheta(o, (uint8_t)(osoite << 1)),
                        I2C_NACK_OSOITE);
        for (size_t i = 0; tila == I2C_OK && i < kirjoitus_n; i++) {
            tila = kuittaus(laheta(o, kirjoitus[i]), I2C_NACK_DATA);
        }
        if (tila == I2C_OK && luku_n > 0 && !start(o)) {
            tila = I2C_AIKARAJA; /* toistettu START */
        }
    }
    if (tila == I2C_OK && luku_n > 0) {
        tila = kuittaus(laheta(o, (uint8_t)(osoite << 1 | 1u)),
                        I2C_NACK_OSOITE);
        for (size_t i = 0; tila == I2C_OK && i < luku_n; i++) {
            if (!vastaanota(o, i + 1 < luku_n, &luku[i])) {
                tila = I2C_AIKARAJA;
            }
        }
    }
    stop(o);
    return tila;
}
// @loppu siirto

// @alku alusta
i2c_tila_t i2c_sbcon_alusta(i2c_sbcon_t *ohjain, sbcon_t *linjat) {
    ohjain->vayla.siirto = siirto;
    ohjain->linjat = linjat;
    ohjain->puolijakso = 4;
    sda(ohjain, 1);
    scl_alas(ohjain);
    /* Laite, joka on jäänyt lähettämään tavua, vapauttaa SDA:n
     * viimeistään yhdeksän kellojakson kuluessa. */
    for (int jakso = 0; jakso < 9 && !lue_sda(ohjain); jakso++) {
        if (!scl_ylos(ohjain)) {
            return I2C_AIKARAJA;
        }
        scl_alas(ohjain);
    }
    if (!lue_sda(ohjain)) {
        return I2C_JUMISSA;
    }
    stop(ohjain);
    return I2C_OK;
}
// @loppu alusta
