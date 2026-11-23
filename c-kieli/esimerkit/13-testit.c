// @alku kehys
#include <ctype.h>
#include <stdio.h>
#include <string.h>

// Minimaalinen testikehys. Epäonnistunut tarkistus tulostaa tiedoston,
// rivin ja lausekkeen, ja testi jatkuu seuraavaan tarkistukseen.
static int tarkistuksia = 0;
static int epaonnistui = 0;

#define TARKISTA(ehto)                                                \
    do {                                                              \
        tarkistuksia++;                                               \
        if (!(ehto)) {                                                \
            epaonnistui++;                                            \
            printf("  EPÄONNISTUI rivillä %d: %s\n", __LINE__, #ehto);\
        }                                                             \
    } while (0)

#define TARKISTA_MJ(saatu, odotettu)                                  \
    TARKISTA(strcmp((saatu), (odotettu)) == 0)

#define AJA(testi)                                                    \
    do {                                                              \
        printf("%s\n", #testi);                                       \
        testi();                                                      \
    } while (0)
// @loppu kehys

// @alku testattava
// Poistaa merkkijonon alusta ja lopusta tyhjät merkit paikallaan.
// Palauttaa osoittimen ensimmäiseen ei-tyhjään merkkiin.
char *siisti(char *s)
{
    while (isspace((unsigned char)*s)) {
        s++;
    }
    size_t n = strlen(s);
    while (n > 0 && isspace((unsigned char)s[n - 1])) {
        s[--n] = '\0';
    }
    return s;
}
// @loppu testattava

// @alku testit
static void testaa_tavallinen(void)
{
    char s[] = "  sana  ";
    TARKISTA_MJ(siisti(s), "sana");
}

static void testaa_reunatapaukset(void)
{
    char tyhja[] = "";
    char valit[] = " \t\n ";
    char sisalla[] = " a b ";
    TARKISTA_MJ(siisti(tyhja), "");
    TARKISTA_MJ(siisti(valit), "");
    TARKISTA_MJ(siisti(sisalla), "a b");
}

int main(void)
{
    AJA(testaa_tavallinen);
    AJA(testaa_reunatapaukset);
    printf("%d tarkistusta, %d epäonnistui\n", tarkistuksia, epaonnistui);
    return epaonnistui == 0 ? 0 : 1;
}
// @loppu testit
