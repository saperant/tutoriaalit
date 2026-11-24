/* Pieni palveluohjelma suojausten tarkasteluun: puskureita, kirjasto-
 * kutsuja ja muotoilua, joihin kääntäjän suojaukset tarttuvat. */
#include <stdio.h>
#include <string.h>

static void tervehdi(const char *nimi)
{
    char viesti[64];
    snprintf(viesti, sizeof viesti, "hei, %s", nimi);
    puts(viesti);
}

int main(int argc, char *argv[])
{
    char nimi[32];
    strncpy(nimi, argc > 1 ? argv[1] : "maailma", sizeof nimi - 1);
    nimi[sizeof nimi - 1] = '\0';
    tervehdi(nimi);
    return 0;
}
