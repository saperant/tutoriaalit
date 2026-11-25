// Assembly-funktio viittaa C:n globaaliin muuttujaan ja kutsuu
// C-funktiota. Ohjelma toimii sekä staattisesti linkitettynä että
// paikkariippumattomana (PIE), koska assembly ei käytä absoluuttisia
// osoitteita.
#include <stdio.h>

#include "laskuri.h"

long laskuri = 40;

long tuplaa(long x) { return 2 * x; }

int main(void)
{
    long tulos = lisaa_ja_tuplaa(2);
    printf("laskuri %ld, tulos %ld\n", laskuri, tulos);
    return (laskuri == 42 && tulos == 84) ? 0 : 1;
}
