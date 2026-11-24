/* Nopeusmonotonisen vuorontamisen analyysi: käyttöastetesti ja
 * vasteaika-analyysi (Joseph & Pandya 1986). Kokonaislukulaskentaa,
 * jotta sama koodi toimii myös ilman liukulukuyksikköä. */
#include "joukko.h"
#include "konsoli.h"

// @alku kayttoaste
unsigned kayttoaste_promille(void) {
    unsigned summa = 0;
    for (unsigned i = 0; i < TEHTAVIA; i++) {
        summa += 1000u * joukko[i].c / joukko[i].t;   /* pyöristys alas */
    }
    return summa;
}

unsigned ll_raja_promille(unsigned n) {
    /* n * (2^(1/n) - 1), laskettu valmiiksi. */
    static const unsigned raja[] = {0, 1000, 828, 779, 756, 743, 734};
    return n < sizeof raja / sizeof raja[0] ? raja[n] : 693;  /* ln 2 */
}
// @loppu kayttoaste

// @alku vasteaika
static TickType_t kattoon(TickType_t a, TickType_t b) {
    return (a + b - 1) / b;
}

TickType_t vasteaika(unsigned i) {
    /* R = C_i + summa tärkeämmistä j: ceil(R / T_j) * C_j */
    TickType_t r = joukko[i].c;
    tulosta("  %s: R = %u", joukko[i].nimi, r);
    for (;;) {
        TickType_t uusi = joukko[i].c;
        for (unsigned j = 0; j < TEHTAVIA; j++) {
            if (joukko[j].prio > joukko[i].prio) {
                uusi += kattoon(r, joukko[j].t) * joukko[j].c;
            }
        }
        if (uusi == r) {
            tulosta("  -> kiintopiste %u <= %u\n", r, joukko[i].t);
            return r;
        }
        tulosta(" -> %u", uusi);
        if (uusi > joukko[i].t) {
            tulosta("  > %u: maaraaika ylittyy\n", joukko[i].t);
            return 0;
        }
        r = uusi;
    }
}
// @loppu vasteaika
