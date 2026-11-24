#ifndef RAPORTTI_H
#define RAPORTTI_H

#include <stddef.h>
#include <stdio.h>

// Kirjoittaa mittaussarjan raportin. Palauttaa 0 tai -1, jos muisti ei
// riitä. Sarjaa ei muuteta.
int kirjoita_raportti(FILE *ulos, const double *x, size_t n);

#endif
