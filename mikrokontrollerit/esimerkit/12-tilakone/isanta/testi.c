/* Tilakoneen testit isäntäkoneella: ajetaan millisekunneissa ilman
 * laitetta, ajastimia tai odottamista. */
#include <stdio.h>
#include <string.h>

#include "tila.h"

static int virheita;

static void odota(const char *nimi, int ehto) {
    printf("%s %s\n", ehto ? "OK  " : "VIRHE", nimi);
    if (!ehto) {
        virheita++;
    }
}

// @alku testit
/* Syöttää raakanäytteet ("0110...", yksi merkki = 10 ms) suotimen
 * kautta tilakoneelle ja palauttaa lopputilan. */
static valo_t aja(const char *naytteet) {
    suodin_t s = {0};
    valo_t v;
    valo_alusta(&v);
    for (size_t i = 0; i < strlen(naytteet); i++) {
        uint32_t nyt = (uint32_t)i * 10u;
        if (suodin_nayte(&s, naytteet[i] == '1')) {
            valo_kasittele(&v, s.vakaa ? T_PAINETTU : T_VAPAUTETTU, nyt);
        }
        valo_kasittele(&v, T_TIKKI, nyt);
    }
    return v;
}

int main(void) {
    odota("lyhyt häiriö ei ole painallus", aja("0001100000").tila == POIS);
    odota("värähtelevä painallus on yksi painallus",
          aja("0101011111111010100000").tila == PAALLA);
    odota("kaksi painallusta: vilkku",
          aja("0011111000000111110000").tila == VILKKU);
    odota("kolme painallusta: pois",
          aja("0011110000111100001111000").tila == POIS);

    char pitka[160];
    memset(pitka, '1', sizeof pitka - 1);   /* 1,59 s pohjassa */
    pitka[sizeof pitka - 1] = '\0';
    memcpy(pitka, "0011110000", 10);        /* ensin päälle */
    valo_t v = aja(pitka);
    odota("pitkä painallus sammuttaa", v.tila == POIS && v.pohjassa);
    odota("vapautus pitkän jälkeen ei vaihda tilaa",
          valo_kasittele(&v, T_VAPAUTETTU, 2000) == 0 && v.tila == POIS);

    printf("%s\n", virheita ? "TESTIT EPÄONNISTUIVAT" : "kaikki kunnossa");
    return virheita != 0;
}
// @loppu testit
