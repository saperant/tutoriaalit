#include <math.h>

#include "tilasto.h"

// Otoskeskihajonta. Käyttää keskiarvoa toisesta jäsenestä.
double hajonta(const double *x, size_t n)
{
    if (n < 2)
        return 0;
    double ka = keskiarvo(x, n), s = 0;
    for (size_t i = 0; i < n; ++i)
        s += (x[i] - ka) * (x[i] - ka);
    return sqrt(s / (double)(n - 1));
}
