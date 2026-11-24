// Tilastofunktiot mittaussarjoille. Kaikki funktiot olettavat, että
// sarjassa on vähintään yksi arvo (n > 0); kutsuja tarkistaa sen.
#ifndef TILASTO_H
#define TILASTO_H

#include <stddef.h>

double keskiarvo(const double *x, size_t n);
double keskihajonta(const double *x, size_t n);
// Mediaani lajittelee taulukon paikallaan.
double mediaani(double *x, size_t n);

#endif
