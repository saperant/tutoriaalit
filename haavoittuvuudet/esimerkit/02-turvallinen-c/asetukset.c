/* Asetustiedoston lukija, jossa on tyypillisiä virheitä kääntäjän ja
 * staattisten analysaattoreiden löydettäväksi. Ohjelmaa ei ajeta. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct asetus {
    char avain[32];
    char *arvo;
};

// @alku lue
int lue_asetus(FILE *tiedosto, struct asetus *asetus)
{
    char rivi[128];
    if (fgets(rivi, sizeof rivi, tiedosto) == NULL) {
        return -1;
    }
    char *erotin = strchr(rivi, '=');
    if (erotin == NULL) {
        return -1;
    }
    int pituus = erotin - rivi;                 /* kapeneva muunnos */
    if (pituus < sizeof asetus->avain) {        /* etumerkkivertailu */
        memcpy(asetus->avain, rivi, pituus);
        asetus->avain[pituus] = '\0';
    }
    asetus->arvo = malloc(strlen(erotin + 1));  /* NUL puuttuu */
    if (asetus->arvo == NULL) {
        return -1;
    }
    strcpy(asetus->arvo, erotin + 1);
    if (asetus->arvo[0] == '\n') {
        free(asetus->arvo);                     /* tyhjä arvo */
    }
    fputs(asetus->arvo, stdout);                /* voi olla vapautettu */
    free(asetus->arvo);
    return atoi(asetus->arvo);
}
// @loppu lue
