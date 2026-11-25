// Tilastofunktioiden yksikkötestit ilman kehystä: assert pysäyttää
// ensimmäiseen virheeseen. (Esimerkki 08-testit esittelee pienen
// testikehyksen.)
#include "tilasto.h"

// Release-käännös määrittelee NDEBUGin, joka tekisi assertista tyhjän:
// testit eivät silloin testaisi mitään.
#undef NDEBUG
#include <assert.h>
#include <math.h>
#include <stdio.h>

static int lahella(double a, double b)
{
    return fabs(a - b) < 1e-9;
}

int main(void)
{
    double x[] = {3.0, 1.0, 2.0};
    assert(lahella(keskiarvo(x, 3), 2.0));
    assert(lahella(keskihajonta(x, 3), 1.0));
    assert(lahella(mediaani(x, 3), 2.0));
    double parillinen[] = {4.0, 1.0, 3.0, 2.0};
    assert(lahella(mediaani(parillinen, 4), 2.5));
    double yksi[] = {7.0};
    assert(lahella(keskihajonta(yksi, 1), 0.0));
    puts("yksikkötestit: OK");
    return 0;
}
