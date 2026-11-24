// Testit, jotka eivät kokeile parillisen pituista sarjaa eivätkä
// yhden arvon hajontaa. Kattavuusraportti paljastaa puutteen.
#include "tilasto.h"

#include <assert.h>
#include <math.h>
#include <stdio.h>

int main(void)
{
    double x[] = {3.0, 1.0, 2.0};
    assert(fabs(keskiarvo(x, 3) - 2.0) < 1e-9);
    assert(fabs(keskihajonta(x, 3) - 1.0) < 1e-9);
    assert(fabs(mediaani(x, 3) - 2.0) < 1e-9);
#ifdef KATTAVAT
    double parillinen[] = {4.0, 1.0, 3.0, 2.0};
    assert(fabs(mediaani(parillinen, 4) - 2.5) < 1e-9);
    double yksi[] = {7.0};
    assert(keskihajonta(yksi, 1) == 0.0);
#endif
    puts("testit läpi");
    return 0;
}
