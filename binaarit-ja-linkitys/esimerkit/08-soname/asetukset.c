#include "asetukset.h"

#ifndef VERSIO
#error "VERSIO puuttuu"
#endif

void asetukset_oletus(struct asetukset *a)
{
    a->nopeus = 120;
    a->tarkkuus = 5;
}

const char *asetukset_versio(void) { return VERSIO; }
