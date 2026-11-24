/* Mittausloki ja sen siirto kehyksinä sarjaportin yli. */
#ifndef LOKI_H
#define LOKI_H

#include <stddef.h>
#include <stdint.h>

#define KEHYS_RAJA   0x7Eu  /* kehyksen alku ja loppu */
#define KEHYS_ESC    0x7Du  /* seuraava tavu XOR 0x20 */
#define KEHYS_TIETUE 0x10u
#define KEHYS_LOPPU  0x11u

void loki_kirjaa(uint32_t aika_ms, int16_t lampo, uint8_t tila);
unsigned loki_maara(void);
void loki_nollaa(void);
void loki_siirra(void);
void laheta_kehys(uint8_t tyyppi, const uint8_t *data, size_t pituus);

#endif
