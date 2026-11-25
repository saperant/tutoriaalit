#ifndef LASKE_H
#define LASKE_H
#include <stddef.h>
#include <stdint.h>

// Palauttaa tavun c esiintymien määrän puskurissa t[0..n).
size_t laske_skalaari(const uint8_t *t, size_t n, uint8_t c);
size_t laske_simd(const uint8_t *t, size_t n, uint8_t c);
#endif
