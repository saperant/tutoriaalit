/* Jaksollinen tehtävä: vTaskDelay ajelehtii, vTaskDelayUntil ei.
 * Tärkeämpi häiriötehtävä viivästyttää molempia, mikä näkyy
 * huojuntana (jitter). */
#include "kide.h"
#include "konsoli.h"
#include "semihost.h"

#define JAKSO   10u
#define KIERROKSIA 8u

static TickType_t viive_alut[KIERROKSIA];
static TickType_t tarkka_alut[KIERROKSIA];

// @alku hairio
/* Tärkein tehtävä: herää 7 tikin välein ja laskee 2 tikkiä. */
static void hairio(void *parametri) {
    (void)parametri;
    TickType_t herays = 0;
    for (;;) {
        kide_kuormita(2);
        vTaskDelayUntil(&herays, 7);
    }
}
// @loppu hairio

// @alku viive
/* Väärin: viive lasketaan siitä, kun työ on tehty. */
static void viive_tehtava(void *parametri) {
    (void)parametri;
    for (unsigned k = 0; k < KIERROKSIA; k++) {
        viive_alut[k] = xTaskGetTickCount();
        kide_kuormita(1);
        vTaskDelay(JAKSO);
    }
    vTaskDelay(portMAX_DELAY);
}
// @loppu viive

// @alku tarkka
/* Oikein: herätys lasketaan edellisestä herätyshetkestä. */
static void tarkka_tehtava(void *parametri) {
    (void)parametri;
    TickType_t herays = xTaskGetTickCount();
    for (unsigned k = 0; k < KIERROKSIA; k++) {
        tarkka_alut[k] = xTaskGetTickCount();
        kide_kuormita(1);
        vTaskDelayUntil(&herays, JAKSO);
    }
    vTaskDelay(portMAX_DELAY);
}
// @loppu tarkka

// @alku raportti
static void raportti(void *parametri) {
    (void)parametri;
    vTaskDelay(KIERROKSIA * JAKSO + 10);
    tulosta("kierros  tavoite  vTaskDelay  DelayUntil  myohassa\n");
    TickType_t pienin = UINT32_MAX, suurin = 0;
    for (unsigned k = 0; k < KIERROKSIA; k++) {
        TickType_t tavoite = k * JAKSO;
        TickType_t myohassa = tarkka_alut[k] - tavoite;
        pienin = myohassa < pienin ? myohassa : pienin;
        suurin = myohassa > suurin ? myohassa : suurin;
        tulosta("%7u  %7u  %10u  %10u  %8u\n", k, tavoite, viive_alut[k],
                tarkka_alut[k], myohassa);
    }
    tulosta("vTaskDelay: %u jaksoa vei %u tikkia (tavoite %u)\n",
            KIERROKSIA - 1, viive_alut[KIERROKSIA - 1] - viive_alut[0],
            (KIERROKSIA - 1) * JAKSO);
    tulosta("vTaskDelayUntil: myohassa %u..%u tikkia, huojunta %u\n",
            pienin, suurin, suurin - pienin);
    lopeta(0);
}
// @loppu raportti

static StaticTask_t tcb[4];
static StackType_t pinot[4][256];

int main(void) {
    konsoli_alusta();
    xTaskCreateStatic(hairio, "hairio", 256, NULL, 3, pinot[0], &tcb[0]);
    xTaskCreateStatic(viive_tehtava, "viive", 256, NULL, 2, pinot[1],
                      &tcb[1]);
    xTaskCreateStatic(tarkka_tehtava, "tarkka", 256, NULL, 1, pinot[2],
                      &tcb[2]);
    xTaskCreateStatic(raportti, "raportti", 256, NULL, 4, pinot[3],
                      &tcb[3]);
    vTaskStartScheduler();
}
