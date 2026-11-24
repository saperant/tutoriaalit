#include <stdio.h>

// Äänikirjaston sisäinen apufunktio samalla nimellä.
void tarkista(const char *nimi) { printf("ääni: tarkistan %s\n", nimi); }

void lataa_aani(const char *nimi) { tarkista(nimi); }
