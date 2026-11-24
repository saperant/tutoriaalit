#include <stdio.h>

#include "asetukset.h"

int main(void)
{
    struct asetukset a;
    asetukset_oletus(&a);
    printf("kirjasto %s: nopeus %d mm/s, tarkkuus %d um\n",
           asetukset_versio(), a.nopeus, a.tarkkuus);
    return 0;
}
