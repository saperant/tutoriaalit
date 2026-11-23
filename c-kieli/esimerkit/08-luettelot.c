#include <stdint.h>
#include <stdio.h>

// @alku enum
enum tila { ODOTTAA, KAYNNISSA, VALMIS, VIRHE };

const char *tilan_nimi(enum tila t)
{
    switch (t) {
    case ODOTTAA: return "odottaa";
    case KAYNNISSA: return "käynnissä";
    case VALMIS: return "valmis";
    case VIRHE: return "virhe";
    }
    return "?";
}
// @loppu enum

// @alku liput
enum oikeus : uint8_t {   // C23: perustyyppi määrätään
    LUKU = 1 << 0,
    KIRJOITUS = 1 << 1,
    SUORITUS = 1 << 2,
};
// @loppu liput

// @alku unioni
typedef enum { LUKU_ARVO, TEKSTI_ARVO, LISTA_ARVO } Arvotyyppi;

typedef struct {
    Arvotyyppi tyyppi;   // kertoo, mikä unionin jäsen on voimassa
    union {
        double luku;
        const char *teksti;
        struct {
            const int *alkiot;
            int pituus;
        } lista;
    };                   // C11: nimetön unioni
} Arvo;

void tulosta_arvo(const Arvo *a)
{
    switch (a->tyyppi) {
    case LUKU_ARVO:
        printf("luku %g\n", a->luku);
        break;
    case TEKSTI_ARVO:
        printf("teksti \"%s\"\n", a->teksti);
        break;
    case LISTA_ARVO:
        printf("lista, %d alkiota\n", a->lista.pituus);
        break;
    }
}
// @loppu unioni

int main(void)
{
    // @alku kaytto
    for (enum tila t = ODOTTAA; t <= VIRHE; ++t) {
        printf("%d = %s\n", t, tilan_nimi(t));
    }

    uint8_t oikeudet = LUKU | KIRJOITUS;
    printf("kirjoitus: %d, suoritus: %d, koko: %zu\n",
           (oikeudet & KIRJOITUS) != 0, (oikeudet & SUORITUS) != 0,
           sizeof(enum oikeus));

    static const int luvut[] = {1, 2, 3};
    Arvo arvot[] = {
        {.tyyppi = LUKU_ARVO, .luku = 2.5},
        {.tyyppi = TEKSTI_ARVO, .teksti = "hei"},
        {.tyyppi = LISTA_ARVO, .lista = {luvut, 3}},
    };
    for (int i = 0; i < 3; ++i) {
        tulosta_arvo(&arvot[i]);
    }
    printf("sizeof(Arvo) = %zu\n", sizeof(Arvo));
    // @loppu kaytto
}
