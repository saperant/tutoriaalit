#include <stdlib.h>

#include "tilasto.h"

static int vertaa(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

double mediaani(double *x, size_t n)
{
    qsort(x, n, sizeof *x, vertaa);
    return n % 2 ? x[n / 2] : (x[n / 2 - 1] + x[n / 2]) / 2;
}
