// Ahne aikataulutus: mahdollisimman monta varausta yhteen saliin, kun
// varaukset eivät saa mennä päällekkäin. Kolme ahnetta sääntöä
// verrataan raakaan hakuun, joka kokeilee kaikki osajoukot.
#include <stdio.h>
#include <stdlib.h>

#include "satunnainen.h"

typedef struct {
    int alku, loppu;            // puoliavoin väli [alku, loppu)
} Varaus;

typedef enum { AIKAISIN_LOPPU, AIKAISIN_ALKU, LYHIN } Saanto;

static int avain(Varaus v, Saanto s)
{
    switch (s) {
    case AIKAISIN_LOPPU: return v.loppu;
    case AIKAISIN_ALKU:  return v.alku;
    case LYHIN:          return v.loppu - v.alku;
    }
    return 0;
}

// @alku ahne
// Käydään varaukset läpi säännön mukaisessa järjestyksessä ja otetaan
// jokainen, joka ei mene päällekkäin jo valittujen kanssa.
static int ahne(Varaus *v, int n, Saanto s)
{
    for (int i = 1; i < n; i++) {           // lisäyslajittelu avaimella
        Varaus x = v[i];
        int j = i - 1;
        while (j >= 0 && avain(v[j], s) > avain(x, s)) {
            v[j + 1] = v[j];
            j--;
        }
        v[j + 1] = x;
    }
    bool valittu[32] = { false };
    int maara = 0;
    for (int i = 0; i < n; i++) {
        bool sopii = true;
        for (int j = 0; j < n && sopii; j++) {
            if (valittu[j] && v[i].alku < v[j].loppu &&
                v[j].alku < v[i].loppu) {
                sopii = false;
            }
        }
        if (sopii) {
            valittu[i] = true;
            maara++;
        }
    }
    return maara;
}
// @loppu ahne

static int raaka(const Varaus *v, int n)
{
    int paras = 0;
    for (unsigned joukko = 0; joukko < (1u << n); joukko++) {
        bool ok = true;
        int koko = 0;
        for (int i = 0; i < n && ok; i++) {
            if (!(joukko >> i & 1)) {
                continue;
            }
            koko++;
            for (int j = i + 1; j < n && ok; j++) {
                if ((joukko >> j & 1) && v[i].alku < v[j].loppu &&
                    v[j].alku < v[i].loppu) {
                    ok = false;
                }
            }
        }
        if (ok && koko > paras) {
            paras = koko;
        }
    }
    return paras;
}

int main(void)
{
    static const char *const nimet[] = {
        "aikaisin loppu", "aikaisin alku", "lyhin",
    };
    // Vastaesimerkit: pitkä varaus alussa ja lyhyt kahden välissä.
    Varaus pitka[] = { { 0, 10 }, { 1, 3 }, { 4, 6 }, { 7, 9 } };
    Varaus lyhyt[] = { { 0, 5 }, { 4, 7 }, { 6, 11 } };
    printf("%-17s %5s %5s\n", "sääntö", "pitkä", "lyhyt");
    for (Saanto s = AIKAISIN_LOPPU; s <= LYHIN; s++) {
        printf("%-14s %5d %5d\n", nimet[s],
               ahne(pitka, 4, s), ahne(lyhyt, 3, s));
    }
    printf("%-14s %5d %5d\n", "optimi", raaka(pitka, 4), raaka(lyhyt, 3));

    // Satunnaistesti: kuinka usein kukin sääntö löytää optimin?
    Satunnainen sat = { 17 };
    int osumia[3] = { 0 };
    enum { KIERROKSIA = 500 };
    for (int k = 0; k < KIERROKSIA; k++) {
        int n = 1 + (int)satunnainen_alle(&sat, 12);
        Varaus v[12];
        for (int i = 0; i < n; i++) {
            v[i].alku = (int)satunnainen_alle(&sat, 20);
            v[i].loppu = v[i].alku + 1 + (int)satunnainen_alle(&sat, 8);
        }
        int optimi = raaka(v, n);
        for (Saanto s = AIKAISIN_LOPPU; s <= LYHIN; s++) {
            osumia[s] += ahne(v, n, s) == optimi;
        }
    }
    for (Saanto s = AIKAISIN_LOPPU; s <= LYHIN; s++) {
        printf("%3d/%d optimaalisia  %s\n", osumia[s], KIERROKSIA,
               nimet[s]);
    }
    return EXIT_SUCCESS;
}
