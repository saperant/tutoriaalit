/* Vieraskirja: lukee kävijöiden nimet riveittäin ja tulostaa yhteenvedon.
 * Tarkoituksella haavoittuva versio: nimi kopioidaan kiinteään puskuriin
 * tarkistamatta pituutta. Makro KORJATTU valitsee korjatun version. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { NIMI_MAX = 16, KAVIJOITA_MAX = 8 };

struct kavija {
    char nimi[NIMI_MAX];
    int kaynnit;
};

static struct kavija *kirja[KAVIJOITA_MAX];
static int kavijoita;

// @alku kirjaa
/* Kirjaa käynnin. Palauttaa 0 tai -1, jos nimeä ei voi tallentaa. */
static int kirjaa(const char *nimi)
{
    for (int i = 0; i < kavijoita; i++) {
        if (strcmp(kirja[i]->nimi, nimi) == 0) {
            kirja[i]->kaynnit++;
            return 0;
        }
    }
    if (kavijoita == KAVIJOITA_MAX) {
        return -1;
    }
    struct kavija *uusi = malloc(sizeof *uusi);
    if (uusi == NULL) {
        return -1;
    }
#ifdef KORJATTU
    if (strlen(nimi) >= sizeof uusi->nimi) {
        free(uusi);
        return -1;                      /* ei mahdu: hylätään */
    }
    memcpy(uusi->nimi, nimi, strlen(nimi) + 1);
#else
    strcpy(uusi->nimi, nimi);           /* VIRHE: pituutta ei tarkisteta */
#endif
    uusi->kaynnit = 1;
    kirja[kavijoita++] = uusi;
    return 0;
}
// @loppu kirjaa

int main(void)
{
    char rivi[128];
    while (fgets(rivi, sizeof rivi, stdin) != NULL) {
        rivi[strcspn(rivi, "\n")] = '\0';
        if (kirjaa(rivi) != 0) {
            printf("hylätty: %.20s...\n", rivi);
        }
    }
    for (int i = 0; i < kavijoita; i++) {
        printf("%-16s %d\n", kirja[i]->nimi, kirja[i]->kaynnit);
        free(kirja[i]);
    }
    return 0;
}
