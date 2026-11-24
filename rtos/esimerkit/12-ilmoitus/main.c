/* Tehtäväilmoitus kevyenä semaforina: ilmoitus on laskuri tehtävän
 * omassa ohjauslohkossa, joten erillistä oliota ei tarvita.
 * ulTaskNotifyTake(pdTRUE, ...) ottaa kaikki kertyneet ilmoitukset
 * kerralla (binäärisemafori), pdFALSE yhden kerrallaan (laskeva). */
#include "kide.h"
#include "konsoli.h"
#include "semihost.h"

static TaskHandle_t kaikki_kerralla, yksi_kerrallaan;

// @alku vastaanottaja
static void vastaanottaja(void *parametri) {
    BaseType_t tyhjenna = parametri != NULL;
    const char *nimi = pcTaskGetName(xTaskGetCurrentTaskHandle());
    for (;;) {
        uint32_t maara = ulTaskNotifyTake(tyhjenna, 5);
        if (maara == 0) {
            tulosta("%3u %s: ei ilmoituksia\n", xTaskGetTickCount(), nimi);
            vTaskDelay(portMAX_DELAY);
        }
        tulosta("%3u %s: ulTaskNotifyTake palautti %u\n",
                xTaskGetTickCount(), nimi, maara);
        kide_kuormita(1);
    }
}
// @loppu vastaanottaja

// @alku lahettaja
static void lahettaja(void *parametri) {
    (void)parametri;
    vTaskDelay(1);
    tulosta("%3u lahettaja: 3 ilmoitusta kummallekin\n",
            xTaskGetTickCount());
    for (unsigned i = 0; i < 3; i++) {
        xTaskNotifyGive(kaikki_kerralla);
        xTaskNotifyGive(yksi_kerrallaan);
    }
    vTaskDelay(12);
    lopeta(0);
}
// @loppu lahettaja

static StaticTask_t tcb[3];
static StackType_t pinot[3][256];

int main(void) {
    konsoli_alusta();
    kaikki_kerralla = xTaskCreateStatic(vastaanottaja, "kerralla", 256,
                                        (void *)1, 1, pinot[0], &tcb[0]);
    yksi_kerrallaan = xTaskCreateStatic(vastaanottaja, "yksitellen", 256,
                                        NULL, 1, pinot[1], &tcb[1]);
    xTaskCreateStatic(lahettaja, "lahettaja", 256, NULL, 3, pinot[2],
                      &tcb[2]);
    vTaskStartScheduler();
}
