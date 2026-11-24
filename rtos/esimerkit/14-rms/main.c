/* Nopeusmonotoninen vuorontaminen: analyysi ennustaa pahimmat
 * vasteajat, ja sama tehtäväjoukko ajetaan Kidessä. Kaikki tehtävät
 * julkaistaan hetkellä 0 (kriittinen hetki), joten havaittu pahin
 * vasteaika on sama kuin analyysin. */
#include "aikajana.h"
#include "joukko.h"
#include "konsoli.h"
#include "semihost.h"

#ifdef YLIKUORMA
#define AJOAIKA 30u
#else
#define AJOAIKA 24u        /* kaksi hyperjaksoa: lcm(4, 6, 12) = 12 */
#endif

static TickType_t pahin[TEHTAVIA];
static unsigned myohassa[TEHTAVIA];

// @alku tehtava
static void jaksollinen(void *parametri) {
    unsigned i = (unsigned)(uintptr_t)parametri;
    TickType_t julkaisu = 0;
    for (;;) {
        kide_kuormita(joukko[i].c);
        TickType_t vaste = xTaskGetTickCount() - julkaisu;
        if (vaste > pahin[i]) {
            pahin[i] = vaste;
        }
        if (vaste > joukko[i].t) {
            myohassa[i]++;        /* määräaika ylittyi */
        }
        vTaskDelayUntil(&julkaisu, joukko[i].t);
    }
}
// @loppu tehtava

static void tuhannesosa(unsigned arvo) {
    tulosta("%u.%03u", arvo / 1000, arvo % 1000);
}

// @alku raportti
static void raportti(void *parametri) {
    (void)parametri;
    vTaskDelay(AJOAIKA);
    aikajana_tulosta(AJOAIKA);
    tulosta("\nkayttoaste U = ");
    tuhannesosa(kayttoaste_promille());
    tulosta(", Liu-Layland-raja = ");
    tuhannesosa(ll_raja_promille(TEHTAVIA));
    tulosta("\nvasteaika-analyysi:\n");
    TickType_t analyysi[TEHTAVIA];
    for (unsigned i = 0; i < TEHTAVIA; i++) {
        analyysi[i] = vasteaika(i);
    }
    tulosta("\ntehtava   C   T  R(analyysi)  R(havaittu)  myohassa\n");
    for (unsigned i = 0; i < TEHTAVIA; i++) {
        tulosta("%s       %2u  %2u  ", joukko[i].nimi, joukko[i].c,
                joukko[i].t);
        if (analyysi[i] == 0) {
            tulosta("    ylittyy");
        } else {
            tulosta("%11u", analyysi[i]);
        }
        tulosta("  %11u  %8u\n", pahin[i], myohassa[i]);
    }
    lopeta(0);
}
// @loppu raportti

static StaticTask_t tcb[TEHTAVIA + 1];
static StackType_t pinot[TEHTAVIA + 1][256];

int main(void) {
    konsoli_alusta();
    for (unsigned i = 0; i < TEHTAVIA; i++) {
        aikajana_lisaa(xTaskCreateStatic(jaksollinen, joukko[i].nimi, 256,
                                         (void *)(uintptr_t)i,
                                         joukko[i].prio, pinot[i],
                                         &tcb[i]));
    }
    xTaskCreateStatic(raportti, "raportti", 256, NULL, 7, pinot[TEHTAVIA],
                      &tcb[TEHTAVIA]);
    vTaskStartScheduler();
}
