// Kohdeohjelma jäljitykseen: lukee asetukset, tarkistaa salasanan ja
// kirjaa yrityksen lokiin.
#include <stdio.h>
#include <string.h>

// Salasana kootaan ajon aikana, joten se ei näy strings-työkalulla.
static void salasana(char *kohde)
{
    static const char osat[] = {'L' ^ 7, 'u' ^ 7, 'm' ^ 7, 'i' ^ 7,
                                '-' ^ 7, '2' ^ 7, '0' ^ 7, '2' ^ 7,
                                '6' ^ 7};
    for (size_t i = 0; i < sizeof osat; i++) {
        kohde[i] = (char)(osat[i] ^ 7);
    }
    kohde[sizeof osat] = '\0';
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "käyttö: %s SALASANA\n", argv[0]);
        return 2;
    }
    char rivi[64] = "";
    FILE *asetukset = fopen("asetukset.conf", "r");
    if (asetukset == NULL || fgets(rivi, sizeof rivi, asetukset) == NULL) {
        fprintf(stderr, "asetukset.conf puuttuu\n");
        return 1;
    }
    fclose(asetukset);
    rivi[strcspn(rivi, "\n")] = '\0';

    char oikea[16];
    salasana(oikea);
    int ok = strcmp(argv[1], oikea) == 0;

    FILE *loki = fopen(rivi, "a");
    if (loki == NULL) {
        return 1;
    }
    fprintf(loki, "kirjautuminen %s\n", ok ? "onnistui" : "epäonnistui");
    fclose(loki);
    puts(ok ? "tervetuloa" : "väärä salasana");
    return ok ? 0 : 1;
}
