// Anturipalvelu, jossa on kaksi vikaa vianetsinnän harjoitteluun.
// Asetustiedoston puuttuessa se kertoo vain, että alustus epäonnistui,
// ja rivi, jossa ei ole =-merkkiä, kaataa sen.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static struct {
    int vali_ms;
    int kerroin;
} asetukset = { .vali_ms = 1000, .kerroin = 1 };

// @alku jasenna
// Jäsentää rivin "nimi=arvo" ja tallentaa arvon asetuksiin.
static int jasenna(char *rivi)
{
    char *erotin = strchr(rivi, '=');
    *erotin = '\0';              // vika: NULL, jos = puuttuu
    int arvo = atoi(erotin + 1);
    if (strcmp(rivi, "vali_ms") == 0) {
        asetukset.vali_ms = arvo;
    } else if (strcmp(rivi, "kerroin") == 0) {
        asetukset.kerroin = arvo;
    } else {
        return -1;
    }
    return 0;
}
// @loppu jasenna

// @alku lue
// Palauttaa 0, -1 (tiedostoa ei saatu auki) tai virheellisen rivin
// numeron.
static int lue_asetukset(const char *polku)
{
    char rivi[64];
    int numero = 0;
    FILE *f = fopen(polku, "r");
    if (f == NULL) {
        return -1;               // vika: syy (errno) jää kertomatta
    }
    while (fgets(rivi, sizeof rivi, f) != NULL) {
        numero++;
        rivi[strcspn(rivi, "\n")] = '\0';
        if (rivi[0] == '\0' || rivi[0] == '#') {
            continue;
        }
        if (jasenna(rivi) != 0) {
            fclose(f);
            return numero;
        }
    }
    fclose(f);
    return 0;
}
// @loppu lue

int main(int argc, char **argv)
{
    const char *polku = argc > 1 ? argv[1] : "/etc/anturi.conf";
    if (lue_asetukset(polku) != 0) {
        fprintf(stderr, "anturi: alustus epaonnistui\n");
        return 1;
    }
    printf("anturi: vali %d ms, kerroin %d\n", asetukset.vali_ms,
           asetukset.kerroin);
    return 0;
}
