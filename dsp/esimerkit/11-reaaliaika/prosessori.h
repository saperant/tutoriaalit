// Lohkoittain toimiva Q1.15-kasittelija: FIR ja vahvistus.
#pragma once
#include <stddef.h>
#include <stdint.h>

// @alku tyyppi
typedef struct {
    const int16_t *h;       // Q1.15-kertoimet
    size_t lkm;
    int16_t *viive;         // 2 * lkm alkiota
    size_t paikka;
    int32_t vahvistus;      // Q4.12: 4096 = 1,0
    unsigned long saturaatiot;
} prosessori_t;
// @loppu tyyppi

int prosessori_alusta(prosessori_t *p, const int16_t *h, size_t lkm,
                      int16_t *puskuri, int32_t vahvistus);
// Reaaliaikaturvallinen: ei muistinvarausta, lukkoja eika I/O:ta.
void prosessori_lohko(prosessori_t *p, const int16_t *x, int16_t *y,
                      size_t n);
