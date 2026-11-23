#include <stdio.h>

// @alku sudenkuoppa
#define NELIO_VAARIN(x) x * x
#define NELIO(x) ((x) * (x))
// @loppu sudenkuoppa

// @alku erikoiset
#define MERKKIJONOKSI(x) #x
#define TARKISTA(ehto)                                              \
    do {                                                            \
        if (!(ehto)) {                                              \
            printf("rivi %d, funktio %s: ehto '%s' ei täyty\n",    \
                   __LINE__, __func__, MERKKIJONOKSI(ehto));        \
        }                                                           \
    } while (0)
// @loppu erikoiset

// @alku generic
#define TYYPIN_NIMI(x) _Generic((x), \
    int: "int",                      \
    double: "double",                \
    const char *: "merkkijono",      \
    default: "muu")
// @loppu generic

// @alku ehdollinen
#ifndef LOKITASO
#define LOKITASO 1
#endif

#if LOKITASO >= 2
#define DEBUG(viesti) printf("debug: %s\n", viesti)
#else
#define DEBUG(viesti) ((void)0)
#endif
// @loppu ehdollinen

int main(void)
{
    // @alku kaytto
    printf("NELIO_VAARIN(1 + 2) = %d\n", NELIO_VAARIN(1 + 2));
    printf("NELIO(1 + 2) = %d\n", NELIO(1 + 2));

    int x = 5;
    TARKISTA(x > 0);
    TARKISTA(x % 2 == 0);

    const char *s = "abc";
    printf("%s %s %s\n", TYYPIN_NIMI(42), TYYPIN_NIMI(2.0),
           TYYPIN_NIMI(s));

    DEBUG("tätä ei tulosteta, koska LOKITASO on 1");
    // @loppu kaytto
}
