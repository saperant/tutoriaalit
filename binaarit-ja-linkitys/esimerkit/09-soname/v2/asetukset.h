#ifndef ASETUKSET_H
#define ASETUKSET_H

// Versio 2: kenttien järjestys vaihtui. Lähdekoodi kääntyy ennallaan,
// mutta binäärirajapinta (ABI) muuttui.
struct asetukset {
    int tarkkuus;    // mikrometreinä
    int nopeus;      // mm/s
};

void asetukset_oletus(struct asetukset *a);
const char *asetukset_versio(void);

#endif
