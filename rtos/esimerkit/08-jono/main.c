/* Tuottaja ja kuluttaja jonon kautta. Tuottaja on nopeampi, joten jono
 * täyttyy: lähetys odottaa enintään aikarajan verran, ja sen jälkeen
 * näyte hylätään. Jono kopioi alkion, joten tuottaja voi käyttää omaa
 * muuttujaansa heti uudelleen. */
#include "kide.h"
#include "konsoli.h"
#include "semihost.h"

// @alku alkio
typedef struct {
    uint32_t numero;
    TickType_t aika;     /* milloin näyte otettiin */
    int32_t arvo;
} nayte_t;

#define JONON_PITUUS 3u
static uint8_t jonon_muisti[JONON_PITUUS * sizeof(nayte_t)];
static StaticQueue_t jonon_tila;
static QueueHandle_t jono;
// @loppu alkio

// @alku tuottaja
static void tuottaja(void *parametri) {
    (void)parametri;
    TickType_t herays = 0;
    for (uint32_t n = 1; n <= 12; n++) {
        nayte_t nayte = {n, xTaskGetTickCount(), (int32_t)(n * n) - 10};
        if (xQueueSend(jono, &nayte, 1) == pdPASS) {
            tulosta("%3u tuottaja: nayte %u jonoon (%u jonossa)\n",
                    xTaskGetTickCount(), n, uxQueueMessagesWaiting(jono));
        } else {
            tulosta("%3u tuottaja: jono taynna, nayte %u hylatty\n",
                    xTaskGetTickCount(), n);
        }
        vTaskDelayUntil(&herays, 2);
    }
    vTaskDelay(portMAX_DELAY);
}
// @loppu tuottaja

// @alku kuluttaja
static void kuluttaja(void *parametri) {
    (void)parametri;
    nayte_t nayte;
    while (xQueueReceive(jono, &nayte, 20) == pdPASS) {
        kide_kuormita(3);   /* käsittely on hitaampaa kuin tuotanto */
        tulosta("%3u kuluttaja: nayte %u (otettu %u) arvo %d\n",
                xTaskGetTickCount(), nayte.numero, nayte.aika, nayte.arvo);
    }
    tulosta("%3u kuluttaja: ei naytteita 20 tikkiin, lopetus\n",
            xTaskGetTickCount());
    lopeta(0);
}
// @loppu kuluttaja

static StaticTask_t tcb[2];
static StackType_t pinot[2][256];

int main(void) {
    konsoli_alusta();
    jono = xQueueCreateStatic(JONON_PITUUS, sizeof(nayte_t), jonon_muisti,
                              &jonon_tila);
    xTaskCreateStatic(tuottaja, "tuottaja", 256, NULL, 2, pinot[0], &tcb[0]);
    xTaskCreateStatic(kuluttaja, "kuluttaja", 256, NULL, 1, pinot[1],
                      &tcb[1]);
    vTaskStartScheduler();
}
