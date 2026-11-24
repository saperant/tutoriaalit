// Sumea testaus (fuzzing): purkajalle syötetään satoja tuhansia
// rikottuja viestejä. Jokainen syöte on omassa tarkan kokoisessa
// varauksessaan, joten AddressSanitizer pysäyttää ohjelman heti, jos
// purkaja lukee yhdenkin tavun liikaa.
#include <stdio.h>
#include <stdlib.h>

#include "tlv.h"
#include "verkko.h"

enum { KIERROKSIA = 100000 };

// @alku mutaatio
// Rikkoo viestin yhdellä neljästä tavasta: bitin käännös, satunnainen
// tavu, katkaisu tai pituuskentän korvaaminen suurella luvulla.
static size_t muuta(uint8_t *b, size_t n, satunnainen *s) {
    size_t i = satunnainen_alle(s, (uint32_t)n);
    switch (satunnainen_alle(s, 4)) {
    case 0:
        b[i] ^= (uint8_t)(1u << satunnainen_alle(s, 8));
        break;
    case 1:
        b[i] = (uint8_t)satunnainen_alle(s, 256);
        break;
    case 2:
        return i;                        // katkaistaan kohdasta i
    default:
        b[i] = 0xff;
        break;
    }
    return n;
}
// @loppu mutaatio

int main(void) {
    mittaus m = {.anturi = "sauna", .lampotila = -1250, .aika = 1764000000};
    uint8_t alkuperainen[64];
    size_t n = koodaa(&m, alkuperainen);

    // @alku silmukka
    satunnainen s = {2026};
    long tulokset[PURKU_TULOKSIA] = {};
    bool vastaa = true;
    for (int k = 0; k < KIERROKSIA; k++) {
        uint8_t muokattu[64];
        memcpy(muokattu, alkuperainen, n);
        size_t pituus = n;
        for (uint32_t j = 1 + satunnainen_alle(&s, 3); j > 0; j--) {
            pituus = muuta(muokattu, pituus > 0 ? pituus : 1, &s);
        }
        uint8_t *syote = (uint8_t *)malloc(pituus > 0 ? pituus : 1);
        memcpy(syote, muokattu, pituus);
        mittaus tulos;
        purkutulos t = pura(syote, pituus, &tulos);
        tulokset[t]++;
        if (t == PURKU_OK) {             // hyväksytty viesti on eheä:
            uint8_t uusi[64];            // koodattuna ja purettuna sama
            mittaus toinen;
            size_t un = koodaa(&tulos, uusi);
            vastaa = vastaa && pura(uusi, un, &toinen) == PURKU_OK &&
                     memcmp(&tulos, &toinen, sizeof tulos) == 0;
        }
        free(syote);
    }
    // @loppu silmukka
    for (int t = 0; t < PURKU_TULOKSIA; t++) {
        printf("%-8s %6ld\n", PURKUTULOS[t], tulokset[t]);
    }
    printf("hyväksytyt viestit eheitä: %s\n", vastaa ? "kyllä" : "ei");
    return 0;
}
