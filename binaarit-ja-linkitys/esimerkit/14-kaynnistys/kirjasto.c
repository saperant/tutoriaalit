#include <stdio.h>

// @alku kirjasto
// Jaetun kirjaston alustus ajetaan ennen ohjelman omia alustuksia.
__attribute__((constructor)) static void kirjasto_alkuun(void)
{
    puts("1. kirjaston konstruktori");
}

__attribute__((destructor)) static void kirjasto_loppuun(void)
{
    puts("8. kirjaston destruktori");
}
// @loppu kirjasto

void kirjasto_kaytossa(void) { puts("4. main kutsuu kirjastoa"); }
