// Virheentarkistus järjestelmäkutsuille. Kaikki esimerkit käyttävät
// tätä otsaketta, jotta virheen käsittely ei peitä itse asiaa.
#ifndef TARKISTA_H
#define TARKISTA_H

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>

// POSIX-kutsut palauttavat virheessä -1 ja asettavat errno-muuttujan.
static inline long tarkista_(long arvo, const char *kutsu, int rivi) {
    if (arvo == -1) {
        fprintf(stderr, "rivi %d: %s: %s\n", rivi, kutsu,
                strerror(errno));
        exit(EXIT_FAILURE);
    }
    return arvo;
}
#define TARKISTA(kutsu) tarkista_((long)(kutsu), #kutsu, __LINE__)

// pthread-funktiot palauttavat virhekoodin suoraan, eivät aseta errnoa.
static inline void tarkista_pt_(int virhe, const char *kutsu, int rivi) {
    if (virhe != 0) {
        fprintf(stderr, "rivi %d: %s: %s\n", rivi, kutsu,
                strerror(virhe));
        exit(EXIT_FAILURE);
    }
}
#define TARKISTA_PT(kutsu) tarkista_pt_((kutsu), #kutsu, __LINE__)

// mmap palauttaa virheessä MAP_FAILED eikä nollaosoitinta.
static inline void *tarkista_map_(void *p, const char *kutsu, int rivi) {
    if (p == MAP_FAILED) {
        fprintf(stderr, "rivi %d: %s: %s\n", rivi, kutsu,
                strerror(errno));
        exit(EXIT_FAILURE);
    }
    return p;
}
#define TARKISTA_MAP(kutsu) tarkista_map_((kutsu), #kutsu, __LINE__)

// printf laskee leveyden tavuina. Leveys, jolla UTF-8-merkkijono
// tasautuu oikein muodossa printf("%-*s", tasaa(s, 20), s).
static inline int tasaa(const char *s, int leveys) {
    for (; *s; s++) {
        leveys += (*s & 0xC0) == 0x80;   // jatkotavu ei vie tilaa
    }
    return leveys;
}

#endif
