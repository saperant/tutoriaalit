#include "tilasto.h"

double keskiarvo(const double *x, size_t n)
{
    double summa = 0;
    for (size_t i = 0; i < n; ++i)
        summa += x[i];
    return n ? summa / (double)n : 0;
}
