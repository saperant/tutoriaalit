#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>

// @alku virhekoodit
typedef enum {
    OK = 0,
    VIRHE_AVAUS,
    VIRHE_MUISTI,
    VIRHE_KIRJOITUS,
} Tulos;

const char *tulos_teksti(Tulos t)
{
    static const char *const tekstit[] = {
        [OK] = "ok",
        [VIRHE_AVAUS] = "tiedoston avaus epäonnistui",
        [VIRHE_MUISTI] = "muisti loppui",
        [VIRHE_KIRJOITUS] = "kirjoitus epäonnistui",
    };
    return tekstit[t];
}
// @loppu virhekoodit

// @alku siivous
// Kopioi tiedoston isoin kirjaimin. Kaikki resurssit vapautetaan
// yhdessä paikassa funktion lopussa.
Tulos kopioi_isoin(const char *lahde, const char *kohde)
{
    Tulos tulos = OK;
    FILE *sisaan = nullptr;
    FILE *ulos = nullptr;
    char *puskuri = nullptr;

    sisaan = fopen(lahde, "r");
    if (sisaan == nullptr) {
        tulos = VIRHE_AVAUS;
        goto siivous;
    }
    ulos = fopen(kohde, "w");
    if (ulos == nullptr) {
        tulos = VIRHE_AVAUS;
        goto siivous;
    }
    puskuri = malloc(4096);
    if (puskuri == nullptr) {
        tulos = VIRHE_MUISTI;
        goto siivous;
    }

    size_t n;
    while ((n = fread(puskuri, 1, 4096, sisaan)) > 0) {
        for (size_t i = 0; i < n; ++i) {
            puskuri[i] = (char)toupper((unsigned char)puskuri[i]);
        }
        if (fwrite(puskuri, 1, n, ulos) != n) {
            tulos = VIRHE_KIRJOITUS;
            goto siivous;
        }
    }

siivous:
    free(puskuri);
    if (ulos != nullptr && fclose(ulos) != 0 && tulos == OK) {
        tulos = VIRHE_KIRJOITUS;
    }
    if (sisaan != nullptr) {
        fclose(sisaan);
    }
    return tulos;
}
// @loppu siivous

int main(void)
{
    // @alku kaytto
    FILE *f = fopen("syote.txt", "w");
    if (f == nullptr) {
        return EXIT_FAILURE;
    }
    fputs("hello, world\n", f);
    fclose(f);

    Tulos t = kopioi_isoin("syote.txt", "tuloste.txt");
    printf("1. kopiointi: %s\n", tulos_teksti(t));

    char rivi[64];
    f = fopen("tuloste.txt", "r");
    if (f != nullptr && fgets(rivi, sizeof rivi, f) != nullptr) {
        printf("   sisältö: %s", rivi);
    }
    if (f != nullptr) {
        fclose(f);
    }

    t = kopioi_isoin("puuttuu.txt", "tuloste.txt");
    printf("2. kopiointi: %s\n", tulos_teksti(t));
    // @loppu kaytto
}
