// Pieni testikehys yhdessä otsakkeessa. Tarkistus kirjaa virheen ja
// jatkaa, jotta yksi ajo näyttää kaikki rikkoutuneet kohdat.
#ifndef TESTI_H
#define TESTI_H

#include <math.h>
#include <stdio.h>

extern int testi_virheet;

#define TARKISTA(ehto)                                                 \
    do {                                                               \
        if (!(ehto)) {                                                 \
            printf("  %s:%d: ei päde: %s\n", __FILE__, __LINE__,       \
                   #ehto);                                             \
            testi_virheet++;                                           \
        }                                                              \
    } while (0)

#define TARKISTA_LAHELLA(saatu, odotettu)                              \
    do {                                                               \
        double s_ = (saatu), o_ = (odotettu);                          \
        if (fabs(s_ - o_) > 1e-9) {                                    \
            printf("  %s:%d: %s = %g, odotettiin %g\n", __FILE__,      \
                   __LINE__, #saatu, s_, o_);                          \
            testi_virheet++;                                           \
        }                                                              \
    } while (0)

typedef struct {
    const char *nimi;
    void (*funktio)(void);
} testi;

// Ajaa testit ja palauttaa ohjelman paluuarvon (0 = kaikki läpi).
int aja_testit(const testi *testit, int maara);

#endif
