// geometria.h: pisteet ja etäisyydet tasossa.
#ifndef GEOMETRIA_H
#define GEOMETRIA_H

#include <stddef.h>

typedef struct {
    double x, y;
} Piste;

// Etäisyyden neliö: vertailuun riittää, eikä neliöjuurta tarvita.
double etaisyys2(Piste a, Piste b);

#endif
