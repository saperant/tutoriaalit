#include <stdio.h>

#include "loki.h"

// @alku oma
// Vahva määrittely korvaa kirjaston heikon oletuksen.
void loki_kohde(const char *rivi)
{
    fprintf(stdout, "sovellus: %s\n", rivi);
}
// @loppu oma
