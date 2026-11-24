// Uudelleenyritys eksponentiaalisesti kasvavalla viiveellä ja täydellä
// satunnaisuudella (full jitter). Aika on simuloitu, joten tulos on
// toistettava eikä esimerkki nuku oikeasti.
#define _GNU_SOURCE
#include "verkko.h"

// @alku viive
// Odotus ennen yritystä k (1, 2, ...): satunnainen väliltä
// [0, min(katto, perus * 2^(k-1))). Satunnaisuus hajauttaa asiakkaat,
// jotka epäonnistuivat samalla hetkellä.
static uint32_t viive_ms(int k, satunnainen *s) {
    uint32_t perus = 100, katto = 5000;
    uint32_t raja = k >= 7 ? katto : perus << (k - 1);
    raja = raja < katto ? raja : katto;
    return satunnainen_alle(s, raja);
}

// Vain ohimenevat virheet kannattaa yrittää uudelleen.
static bool ohimeneva(int virhe) {
    return virhe == ECONNREFUSED || virhe == ETIMEDOUT ||
           virhe == ECONNRESET || virhe == EAGAIN;
}
// @loppu viive

// Simuloitu palvelu: vastaa vasta, kun se on käynnistynyt hetkellä 1 s.
static int kutsu(uint32_t nyt_ms) {
    return nyt_ms < 1000 ? ECONNREFUSED : 0;
}

int main(void) {
    // @alku silmukka
    satunnainen s = {99};
    uint32_t nyt = 0, maaraaika = 10000;   // koko operaation aikaraja
    for (int k = 1; k <= 8; k++) {
        int virhe = kutsu(nyt);
        printf("t = %4u ms, yritys %d: %s\n", nyt, k,
               virhe ? strerrorname_np(virhe) : "onnistui");
        if (virhe == 0 || !ohimeneva(virhe)) {
            break;
        }
        uint32_t odotus = viive_ms(k, &s);
        if (nyt + odotus > maaraaika) {
            puts("aikaraja: luovutetaan");
            break;
        }
        nyt += odotus;
    }
    // @loppu silmukka

    // @alku lauma
    // 1000 asiakasta menettää yhteyden samalla hetkellä. Montako niistä
    // osuu neljännellä yrityksellään samaan 50 ms:n jaksoon?
    for (int satunnaisesti = 0; satunnaisesti <= 1; satunnaisesti++) {
        int jaksot[200] = {};            // 10 s 50 ms:n jaksoina
        for (int a = 0; a < 1000; a++) {
            uint32_t t = 0;
            for (int k = 1; k <= 4; k++) {
                t += satunnaisesti ? viive_ms(k, &s) : 100u << (k - 1);
            }
            jaksot[t / 50]++;
        }
        int pahin = 0;
        for (int j = 0; j < 200; j++) {
            pahin = jaksot[j] > pahin ? jaksot[j] : pahin;
        }
        printf("%s: pahimmassa jaksossa %d yritystä\n",
               satunnaisesti ? "täysi satunnaisuus" : "ilman satunnaisuutta",
               pahin);
    }
    // @loppu lauma
    return 0;
}
