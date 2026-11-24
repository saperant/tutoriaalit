// stdio-puskurin vaikutus: kuinka monta kirjoituskutsua tavutason
// tulostus aiheuttaa. fopencookie ohjaa virran omaan funktioon, joka
// laskee kutsut write-järjestelmäkutsun sijaan.
#define _GNU_SOURCE
#include <stdio.h>

#include "tarkista.h"

// @alku laskuri
typedef struct {
    int kutsuja;
    size_t tavuja;
} laskuri_t;

static ssize_t kirjoita(void *ev, const char *data, size_t n) {
    (void)data;
    laskuri_t *l = ev;
    l->kutsuja++;
    l->tavuja += n;
    return (ssize_t)n;
}

static void kokeile(const char *nimi, int tila, size_t koko) {
    laskuri_t l = {};
    FILE *f = fopencookie(&l, "w",
                          (cookie_io_functions_t){.write = kirjoita});
    // glibc ei huomioi kokoa, jos puskuria ei anna itse.
    static char puskuri[65536];
    setvbuf(f, tila == _IONBF ? nullptr : puskuri, tila, koko);
    for (int rivi = 0; rivi < 100; rivi++) {
        for (int i = 0; i < 99; i++) {
            fputc('x', f);
        }
        fputc('\n', f);
    }
    fclose(f);
    printf("%-*s kutsuja %5d, tavuja %zu\n", tasaa(nimi, 20), nimi,
           l.kutsuja, l.tavuja);
}
// @loppu laskuri

int main(void) {
    // @alku tilat
    kokeile("täysi puskuri 4096", _IOFBF, 4096);
    kokeile("täysi puskuri 65536", _IOFBF, 65536);
    kokeile("rivipuskuri", _IOLBF, 4096);
    kokeile("ei puskuria", _IONBF, 0);
    // @loppu tilat
    return 0;
}
