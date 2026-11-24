#ifndef TUNNISTUS_H
#define TUNNISTUS_H
#include <stddef.h>
#include <stdint.h>
int avx2_kaytettavissa(void);
size_t laske(const uint8_t *t, size_t n, uint8_t c);
#endif
