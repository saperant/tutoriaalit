/* Lisäosarekisteri, jossa funktiot tallennetaan yleisinä osoittimina.
 * Tarkoituksella virheellinen: lisäosa haetaan väärällä tyypillä, jolloin
 * epäsuora kutsu menee funktioon, jonka tyyppi on eri. Juuri tällaisen
 * kutsun ohjausvuon eheyden tarkistus (CFI) pysäyttää. */
#include <stdio.h>
#include <string.h>

typedef void (*yleinen_t)(void);
typedef int (*komento_t)(const char *argumentti);
typedef double (*muunnin_t)(double arvo);

static int tervehdi(const char *nimi)
{
    return printf("hei, %s\n", nimi) < 0 ? -1 : 0;
}

static double celsius(double fahrenheit)
{
    return (fahrenheit - 32.0) * 5.0 / 9.0;
}

struct lisaosa {
    const char *nimi;
    yleinen_t funktio;
};

static const struct lisaosa rekisteri[] = {
    {"tervehdi", (yleinen_t)(void *)tervehdi},
    {"celsius", (yleinen_t)(void *)celsius},
};

static yleinen_t hae(const char *nimi)
{
    for (size_t i = 0; i < sizeof rekisteri / sizeof rekisteri[0]; i++) {
        if (strcmp(rekisteri[i].nimi, nimi) == 0) {
            return rekisteri[i].funktio;
        }
    }
    return NULL;
}

// @alku kutsu
/* Ajaa komennon. VIRHE: lisäosan tyyppiä ei tarkisteta, joten
 * "celsius" kutsutaan ikään kuin se olisi komento. */
static int aja_komento(const char *nimi, const char *argumentti)
{
    yleinen_t funktio = hae(nimi);
    if (funktio == NULL) {
        return -1;
    }
    komento_t komento = (komento_t)(void *)funktio;
    return komento(argumentti);
}
// @loppu kutsu

int main(int argc, char *argv[])
{
    const char *nimi = argc > 1 ? argv[1] : "tervehdi";
    if (aja_komento(nimi, "aino") != 0) {
        fprintf(stderr, "komento epäonnistui\n");
        return 1;
    }
    muunnin_t muunna = (muunnin_t)(void *)hae("celsius");
    printf("212 F = %.0f C\n", muunna(212.0));
    return 0;
}
