/* Laskeva semafori resurssien laskijana: kaksi tulostinta, neljä
 * tehtävää. Tulostus on odottamista (laite tekee työn), joten tehtävä
 * nukkuu tulostimen varattuaan. Vapautuvan tulostimen saa tärkein
 * odottaja, ei ensimmäisenä saapunut. */
#include "kide.h"
#include "konsoli.h"
#include "semihost.h"

static StaticSemaphore_t tulostimet_tila;
static SemaphoreHandle_t tulostimet;

typedef struct {
    TickType_t saapuu;   /* milloin tehtävä pyytää tulostinta */
    TickType_t kesto;    /* kauanko tulostus kestää */
} tyo_t;

// @alku tulostus
static void tulostustyo(void *parametri) {
    const tyo_t *tyo = parametri;
    const char *nimi = pcTaskGetName(xTaskGetCurrentTaskHandle());
    vTaskDelay(tyo->saapuu);
    tulosta("%3u %s pyytaa tulostinta\n", xTaskGetTickCount(), nimi);
    if (xSemaphoreTake(tulostimet, 10) != pdPASS) {
        tulosta("%3u %s luovutti\n", xTaskGetTickCount(), nimi);
        vTaskDelay(portMAX_DELAY);
    }
    tulosta("%3u %s tulostaa (vapaana %u)\n", xTaskGetTickCount(), nimi,
            uxQueueMessagesWaiting(tulostimet));
    vTaskDelay(tyo->kesto);            /* laite tulostaa */
    xSemaphoreGive(tulostimet);
    tulosta("%3u %s vapautti tulostimen\n", xTaskGetTickCount(), nimi);
    vTaskDelay(portMAX_DELAY);
}
// @loppu tulostus

static const tyo_t tyot[] = {{1, 4}, {1, 6}, {2, 3}, {3, 3}};

static StaticTask_t tcb[5];
static StackType_t pinot[5][256];

static void valvoja(void *parametri) {
    (void)parametri;
    vTaskDelay(15);
    lopeta(0);
}

int main(void) {
    konsoli_alusta();
    tulostimet = xSemaphoreCreateCountingStatic(2, 2, &tulostimet_tila);
    static const char *const nimet[] = {"T1", "T2", "T3", "T4"};
    for (unsigned i = 0; i < 4; i++) {   /* T4 on tärkein */
        xTaskCreateStatic(tulostustyo, nimet[i], 256, (void *)&tyot[i],
                          1 + i, pinot[i], &tcb[i]);
    }
    xTaskCreateStatic(valvoja, "valvoja", 256, NULL, 7, pinot[4], &tcb[4]);
    vTaskStartScheduler();
}
