/* Liukuva keskiarvo. */
#ifndef SUODATIN_H
#define SUODATIN_H

#include <stddef.h>
#include <stdint.h>

int16_t suodata(const int16_t *naytteet, size_t n, size_t ikkuna,
                int16_t *tulos);

#endif
