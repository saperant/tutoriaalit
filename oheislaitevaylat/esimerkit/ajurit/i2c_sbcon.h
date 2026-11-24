/* I2C-väyläohjain SBCon-lohkolle: ohjelma tuottaa jokaisen SCL- ja
 * SDA-muutoksen itse ("bit-bang"). */
#ifndef I2C_SBCON_H
#define I2C_SBCON_H

#include "i2c.h"
#include "mps2.h"

// @alku ohjain
typedef struct {
    i2c_vayla_t vayla; /* ensimmäisenä: &ohjain.vayla == &ohjain */
    sbcon_t *linjat;
    unsigned puolijakso; /* viivesilmukan kierroksia */
} i2c_sbcon_t;

/* Alustaa ohjaimen ja vapauttaa väylän, jos laite on jäänyt pitämään
 * SDA:ta alhaalla (esim. nollauksen keskeyttämä lukusiirto). */
i2c_tila_t i2c_sbcon_alusta(i2c_sbcon_t *ohjain, sbcon_t *linjat);
// @loppu ohjain

#endif
