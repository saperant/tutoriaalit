#include <stdio.h>

#include "tilasto.h"

int main(void)
{
    const double mittaukset[] = {20.5, 21.0, 19.8, 22.1, 20.9};
    size_t n = sizeof mittaukset / sizeof mittaukset[0];
    printf("keskiarvo %.2f, hajonta %.2f\n", keskiarvo(mittaukset, n),
           hajonta(mittaukset, n));
    return 0;
}
