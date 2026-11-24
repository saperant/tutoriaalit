// Lukujen 07 ja 08 yhteinen protokolla ja kuormittaja. Pyyntö on rivi
// "NELIO x" ja vastaus rivi "x*x". Kuormittaja avaa monta yhteyttä
// yhtä aikaa ja tarkistaa jokaisen vastauksen.
#ifndef NELIO_H
#define NELIO_H

#include "verkko.h"

// @alku yhteys
typedef struct {
    int fd;
    char sisaan[128];                    // vajaa rivi odottaa jatkoa
    size_t n;
} yhteys;

// Käsittelee puskurin kokonaiset rivit ja vastaa niihin. Palauttaa
// käsiteltyjen pyyntöjen määrän tai -1 protokollavirheessä. Vastaukset
// ovat pieniä, joten ne mahtuvat lähetyspuskuriin (luku 8 käsittelee
// tilanteen, jossa eivät mahdu).
static inline int kasittele_rivit(yhteys *y) {
    int pyyntoja = 0;
    char *alku = y->sisaan, *lf;
    while ((lf = (char *)memchr(alku, '\n',
                                y->n - (size_t)(alku - y->sisaan)))) {
        *lf = '\0';
        long x;
        if (sscanf(alku, "NELIO %ld", &x) != 1) {
            return -1;
        }
        char vastaus[32];
        int k = snprintf(vastaus, sizeof vastaus, "%ld\n", x * x);
        if (kirjoita_kaikki(y->fd, vastaus, (size_t)k) == -1) {
            return -1;
        }
        pyyntoja++;
        alku = lf + 1;
    }
    y->n -= (size_t)(alku - y->sisaan);
    memmove(y->sisaan, alku, y->n);      // vajaa rivi puskurin alkuun
    return y->n == sizeof y->sisaan ? -1 : pyyntoja;
}
// @loppu yhteys

// Lukee yhden vastausrivin tavu kerrallaan (yksinkertainen, hidas).
static inline long lue_vastaus(int fd) {
    char rivi[32];
    size_t n = 0;
    while (n < sizeof rivi - 1 && recv(fd, rivi + n, 1, 0) == 1 &&
           rivi[n] != '\n') {
        n++;
    }
    rivi[n] = '\0';
    return strtol(rivi, nullptr, 10);
}

// @alku kuormita
// Avaa yhteydet ja lähettää kierroksittain pyynnön jokaiseen ennen kuin
// lukee vastaukset, joten palvelimen on palveltava kaikkia yhtä aikaa.
static inline int kuormita(uint16_t portti, int yhteyksia, int kierroksia) {
    int *fd = (int *)malloc((size_t)yhteyksia * sizeof *fd);
    for (int i = 0; i < yhteyksia; i++) {
        fd[i] = yhdista(portti);
    }
    int virheita = 0;
    for (int k = 0; k < kierroksia; k++) {
        for (int i = 0; i < yhteyksia; i++) {
            char pyynto[32];
            int n = snprintf(pyynto, sizeof pyynto, "NELIO %d\n", i * 100 + k);
            TARKISTA(kirjoita_kaikki(fd[i], pyynto, (size_t)n));
        }
        for (int i = 0; i < yhteyksia; i++) {
            long x = i * 100 + k;
            virheita += lue_vastaus(fd[i]) != x * x;
        }
    }
    for (int i = 0; i < yhteyksia; i++) {
        close(fd[i]);
    }
    free(fd);
    return virheita;
}
// @loppu kuormita

#endif
