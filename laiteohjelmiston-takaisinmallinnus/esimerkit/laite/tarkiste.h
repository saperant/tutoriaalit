/* Tarkisteet: CRC-32 (IEEE 802.3, sama kuin zlib) ja CRC-16/CCITT. */
#ifndef TARKISTE_H
#define TARKISTE_H

#include <stddef.h>
#include <stdint.h>

uint32_t crc32(const void *data, size_t pituus);
uint16_t crc16_ccitt(const uint8_t *data, size_t pituus);

#endif
