#include <stdio.h>

// @alku piilo
// Sisäinen funktio piilotetaan: se ei ole kirjaston rajapintaa.
__attribute__((visibility("hidden")))
void tarkista(const char *nimi) { printf("ääni: tarkistan %s\n", nimi); }

void lataa_aani(const char *nimi) { tarkista(nimi); }
// @loppu piilo
