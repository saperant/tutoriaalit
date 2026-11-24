/* Jaksollisten tehtävien ajoitus simuloidulla kellolla. */
#ifndef TEHTAVAT_H
#define TEHTAVAT_H

#include <stdint.h>

#define TIKKI_MS 100u

void ajoita(uint32_t kesto_ms);
uint32_t ajoaika_ms(void);

#endif
