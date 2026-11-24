#include <stdio.h>

// Rakennushetki ohjelman versiotietoihin. Ilman SOURCE_DATE_EPOCH-
// muuttujaa jokainen rakennus tuottaa eri binäärin.
int main(void)
{
    printf("rakennettu %s %s\n", __DATE__, __TIME__);
    return 0;
}
