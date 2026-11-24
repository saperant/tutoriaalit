#include "tilasto.h"

#include <math.h>
#include <stdlib.h>

double keskiarvo(const double *x, size_t n)
{
    double summa = 0.0;
    for (size_t i = 0; i < n; i++)
        summa += x[i];
    return summa / (double)n;
}

double keskihajonta(const double *x, size_t n)
{
    if (n < 2)
        return 0.0;
    double ka = keskiarvo(x, n);
    double nelio = 0.0;
    for (size_t i = 0; i < n; i++)
        nelio += (x[i] - ka) * (x[i] - ka);
    return sqrt(nelio / (double)(n - 1));
}

static int vertaa(const void *a, const void *b)
{
    double x = *(const double *)a;
    double y = *(const double *)b;
    return (x > y) - (x < y);
}

double mediaani(double *x, size_t n)
{
    qsort(x, n, sizeof *x, vertaa);
    if (n % 2 == 1)
        return x[n / 2];
    return (x[n / 2 - 1] + x[n / 2]) / 2.0;
}
