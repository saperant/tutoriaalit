/* XTEA-lohkosalain (64-bittinen lohko, 128-bittinen avain). */
#ifndef XTEA_H
#define XTEA_H

#include <stdint.h>

void xtea_pura(uint32_t lohko[2], const uint32_t avain[4]);

#endif
