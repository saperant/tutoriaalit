#include <stdio.h>

#include "suodin.hpp"

int main(void)
{
    const double mittaukset[] = {20.5, 21.0, 22.1, 20.8};
    printf("keskiarvo %.2f\n", suodin_keskiarvo(mittaukset, 4));
    return 0;
}
