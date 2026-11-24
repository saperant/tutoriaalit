#include <stdio.h>

#include "yksikot.h"

int main(void)
{
    printf("yksikot %s: 37 C = %.1f F\n", yksikot_versio(),
           fahrenheit(37));
    return 0;
}
