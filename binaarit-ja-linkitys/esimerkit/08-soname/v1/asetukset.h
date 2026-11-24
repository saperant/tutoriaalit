#ifndef ASETUKSET_H
#define ASETUKSET_H

// Versio 1: rakenteen kentät tässä järjestyksessä.
struct asetukset {
    int nopeus;      // mm/s
    int tarkkuus;    // mikrometreinä
};

void asetukset_oletus(struct asetukset *a);
const char *asetukset_versio(void);

#endif
