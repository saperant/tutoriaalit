#ifndef TILASTO_H
#define TILASTO_H

#include <stddef.h>

double keskiarvo(const double *x, size_t n);
double hajonta(const double *x, size_t n);
double mediaani(double *x, size_t n);

#endif
