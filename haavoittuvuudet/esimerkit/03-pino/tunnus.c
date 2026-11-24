/* Kirjautumistunnuksen tarkistus. Tarkoituksella haavoittuva:
 * lue_rivi kopioi syötettä puskuriin tietämättä puskurin kokoa. */
#include <stdio.h>
#include <string.h>

// @alku lue
/* VIRHE: rajapinta ei kerro puskurin kokoa, joten funktio ei voi
 * tarkistaa sitä (vrt. gets, joka poistettiin standardista C11:ssä). */
static void lue_rivi(char *kohde)
{
    int merkki;
    while ((merkki = getchar()) != EOF && merkki != '\n') {
        *kohde++ = (char)merkki;
    }
    *kohde = '\0';
}

static int tarkista(void)
{
    char tunnus[16];
    lue_rivi(tunnus);
    return strcmp(tunnus, "operaattori") == 0;
}
// @loppu lue

// @alku korjattu
/* Korjattu: koko kulkee osoittimen mukana, ja ylipitkä rivi hylätään
 * kokonaan sen sijaan, että se katkaistaisiin hiljaa. */
static bool lue_rivi_turvallisesti(char *kohde, size_t koko)
{
    if (fgets(kohde, (int)koko, stdin) == NULL) {
        return false;
    }
    size_t pituus = strcspn(kohde, "\n");
    if (kohde[pituus] != '\n' && !feof(stdin)) {
        return false;                   /* rivi ei mahtunut */
    }
    kohde[pituus] = '\0';
    return true;
}
// @loppu korjattu

int main(int argc, char *argv[])
{
    (void)argv;
    if (argc > 1) {
        char tunnus[16];
        bool ok = lue_rivi_turvallisesti(tunnus, sizeof tunnus);
        puts(ok ? "tunnus luettu" : "tunnus hylätty: liian pitkä");
        return ok ? 0 : 1;
    }
    puts(tarkista() ? "tervetuloa" : "tuntematon tunnus");
    return 0;
}
