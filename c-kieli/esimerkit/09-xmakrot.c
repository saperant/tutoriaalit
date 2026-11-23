#include <stdio.h>

// @alku xmakro
// Virhekoodit luetellaan kerran. Sama lista tuottaa sekä luettelon että
// kuvaustaulukon, joten ne eivät voi joutua epäsynkroniin.
#define VIRHEET(X)                                   \
    X(OK, "onnistui")                                \
    X(EI_TIEDOSTOA, "tiedostoa ei löydy")            \
    X(EI_OIKEUKSIA, "ei käyttöoikeutta")             \
    X(MUISTI, "muisti loppui")

#define LUETTELO(nimi, kuvaus) VIRHE_##nimi,
typedef enum { VIRHEET(LUETTELO) VIRHEITA } Virhe;
#undef LUETTELO

#define KUVAUS(nimi, kuvaus) [VIRHE_##nimi] = kuvaus,
static const char *const kuvaukset[] = { VIRHEET(KUVAUS) };
#undef KUVAUS

#define NIMI(nimi, kuvaus) [VIRHE_##nimi] = #nimi,
static const char *const nimet[] = { VIRHEET(NIMI) };
#undef NIMI
// @loppu xmakro

int main(void)
{
    // @alku kaytto
    static_assert(sizeof kuvaukset / sizeof kuvaukset[0] == VIRHEITA);
    for (Virhe v = VIRHE_OK; v < VIRHEITA; ++v) {
        printf("%d %-13s %s\n", v, nimet[v], kuvaukset[v]);
    }
    // @loppu kaytto
}
