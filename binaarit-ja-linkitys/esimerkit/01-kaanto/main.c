#include <stdio.h>

#include "laskin.h"

int main(void)
{
    long summa = loppusumma(1290, 3, 10);
    printf("loppusumma: %ld.%02ld euroa\n", summa / 100, summa % 100);
    return 0;
}
