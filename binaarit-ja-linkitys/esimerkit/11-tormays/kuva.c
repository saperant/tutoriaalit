#include <stdio.h>

// @alku kuva
// Kuvakirjaston sisäinen apufunktio, joka jäi vahingossa julkiseksi.
void tarkista(const char *nimi) { printf("kuva: tarkistan %s\n", nimi); }

void lataa_kuva(const char *nimi) { tarkista(nimi); }
// @loppu kuva
