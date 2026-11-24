// Isot kirjaimet: piilotettu neliöllinen silmukka ja sen korjaus.
#define _POSIX_C_SOURCE 200809L
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "mittari.h"
#include "satunnainen.h"

// @alku hidas
// Muuttaa ASCII-kirjaimet isoiksi. Ehto laskee strlen-funktion joka
// kierroksella: silmukka kirjoittaa merkkijonoon, joten kääntäjä ei
// voi todistaa pituuden pysyvän samana.
static void isoiksi_hidas(char *s)
{
    for (size_t i = 0; i < strlen(s); i++) {
        s[i] = (char)toupper((unsigned char)s[i]);
    }
}
// @loppu hidas

// @alku nopea
static void isoiksi(char *s)
{
    size_t n = strlen(s);
    for (size_t i = 0; i < n; i++) {
        s[i] = (char)toupper((unsigned char)s[i]);
    }
}
// @loppu nopea

// Tekstiä, jossa on pieniä kirjaimia ja välilyöntejä.
static char *luo_teksti(size_t n, uint64_t siemen)
{
    char *s = malloc(n + 1);
    if (s == NULL) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }
    Satunnainen r = {siemen};
    for (size_t i = 0; i < n; i++) {
        uint32_t k = satunnainen_alle(&r, 32);
        s[i] = k < 26 ? (char)('a' + k) : ' ';
    }
    s[n] = '\0';
    return s;
}

typedef struct {
    char *teksti;
    void (*muunna)(char *);
} Tila;

static void aja(void *p)
{
    Tila *t = p;
    t->muunna(t->teksti);
    kayta(t->teksti);
}

static void mittaa_kaikki(void)
{
    printf("isot kirjaimet (aika kasvaa: hidas ~n^2, nopea ~n)\n");
    for (size_t n = 10000; n <= 80000; n *= 2) {
        char *s = luo_teksti(n, 1);
        Tila hidas = {s, isoiksi_hidas};
        Tila nopea = {s, isoiksi};
        Tilasto th = mittaa(aja, &hidas, 5);
        Tilasto tn = mittaa(aja, &nopea, 5);
        printf(" n = %zu\n", n);
        tulosta_mittaus("hidas", th, 0);
        tulosta_mittaus("nopea", tn, th.mediaani);
        free(s);
    }
}

int main(int argc, char **argv)
{
    if (mittaustila(argc, argv)) {
        mittaa_kaikki();
        return 0;
    }
    // @alku testi
    // Toiminnallinen testi: molemmat versiot antavat saman tuloksen.
    char *a = luo_teksti(1000, 1);
    char *b = luo_teksti(1000, 1);
    isoiksi_hidas(a);
    isoiksi(b);
    printf("tulokset samat: %s\n", strcmp(a, b) == 0 ? "kylla" : "ei");
    printf("alku: \"%.40s\"\n", a);
    // @loppu testi
    free(a);
    free(b);
    return 0;
}
