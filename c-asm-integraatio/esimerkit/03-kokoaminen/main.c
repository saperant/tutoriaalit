// Erillinen assembly-tiedosto linkitettynä C-ohjelmaan. Itse funktio
// on yksinkertainen; esimerkin asia on tarkistus.sh:ssa: mitä
// tapahtuu, kun .S-tiedosto kootaan väärin tai siitä puuttuu
// pinomerkintä.
#include <stdio.h>

long kolminkertaista(long x);

int main(void) {
    printf("kolminkertaista(14) = %ld\n", kolminkertaista(14));
    return 0;
}
