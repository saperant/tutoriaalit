/* Aikajana ASCII-kaaviona (ks. aikajana.h). */
#include "aikajana.h"
#include "konsoli.h"

#define RIVEJA 8u

static TaskHandle_t ajaja[AIKAJANA_TIKIT];   /* ajaja[i]: väli [i, i+1) */
static TaskHandle_t rivit[RIVEJA];
static unsigned riveja;
static TaskHandle_t seurattu;                /* prioriteettirivi */
static unsigned char prioriteetti[AIKAJANA_TIKIT];

void vApplicationTickHook(void) {
    TickType_t i = xTaskGetTickCount() - 1u;
    if (i < AIKAJANA_TIKIT) {
        ajaja[i] = xTaskGetCurrentTaskHandle();
        if (seurattu != NULL) {
            prioriteetti[i] = (unsigned char)uxTaskPriorityGet(seurattu);
        }
    }
}

void aikajana_lisaa(TaskHandle_t tehtava) {
    if (riveja < RIVEJA) {
        rivit[riveja++] = tehtava;
    }
}

void aikajana_seuraa_prioriteettia(TaskHandle_t tehtava) {
    seurattu = tehtava;
}

static void nimi(const char *teksti) {
    unsigned n = 0;
    for (; teksti[n] != '\0' && n < 9; n++) {
        konsoli_merkki(teksti[n]);
    }
    for (; n < 10; n++) {
        konsoli_merkki(' ');
    }
}

void aikajana_tulosta(TickType_t loppu) {
    if (loppu > AIKAJANA_TIKIT) {
        loppu = AIKAJANA_TIKIT;
    }
    nimi("tikki");
    for (TickType_t i = 0; i < loppu; i += 10) {   /* kymmenet */
        konsoli_kirjoita(i == 0 ? "0" : "         ");
        if (i > 0) {
            konsoli_merkki((char)('0' + i / 10 % 10));
        }
    }
    konsoli_merkki('\n');
    nimi("");
    for (TickType_t i = 0; i < loppu; i++) {
        konsoli_merkki((char)('0' + i % 10));
    }
    konsoli_merkki('\n');
    for (unsigned r = 0; r < riveja; r++) {
        nimi(pcTaskGetName(rivit[r]));
        for (TickType_t i = 0; i < loppu; i++) {
            konsoli_merkki(ajaja[i] == rivit[r] ? '#' : '.');
        }
        konsoli_merkki('\n');
    }
    if (seurattu != NULL) {
        nimi("prio");
        for (TickType_t i = 0; i < loppu; i++) {
            konsoli_merkki((char)('0' + prioriteetti[i] % 10));
        }
        tulosta("  (%s)\n", pcTaskGetName(seurattu));
    }
}

void aikajana_tilastot(void) {
    nimi("tehtava");
    konsoli_kirjoita("prio  ajoaika  valinnat\n");
    for (unsigned r = 0; r < riveja; r++) {
        nimi(pcTaskGetName(rivit[r]));
        tulosta("%4u  %7u  %8u\n", uxTaskPriorityGet(rivit[r]),
                ulTaskGetRunTimeCounter(rivit[r]), rivit[r]->vaihdot);
    }
}
