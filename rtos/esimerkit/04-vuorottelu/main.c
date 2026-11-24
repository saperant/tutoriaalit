/* Saman prioriteetin tehtävät: vuorottelu tikin välein
 * (configUSE_TIME_SLICING=1) tai valmiiksi asti (=0). Muunnelma
 * 04-vuorottelu-ei käännetään valitsimella
 * -DconfigUSE_TIME_SLICING=0. */
#include "aikajana.h"
#include "kide.h"
#include "konsoli.h"
#include "semihost.h"

// @alku laskija
static void laskija(void *parametri) {
    (void)parametri;
    kide_kuormita(4);
    tulosta("%3u %s valmis\n", xTaskGetTickCount(),
            pcTaskGetName(xTaskGetCurrentTaskHandle()));
    vTaskDelay(portMAX_DELAY);
}
// @loppu laskija

static StaticTask_t tcb[4];
static StackType_t pinot[4][256];

static void valvoja(void *parametri) {
    (void)parametri;
    vTaskDelay(14);
    tulosta("\n");
    aikajana_tulosta(14);
    lopeta(0);
}

int main(void) {
    konsoli_alusta();
    static const char *const nimet[] = {"A", "B", "C"};
    for (unsigned i = 0; i < 3; i++) {
        aikajana_lisaa(xTaskCreateStatic(laskija, nimet[i], 256, NULL, 1,
                                         pinot[i], &tcb[i]));
    }
    xTaskCreateStatic(valvoja, "valvoja", 256, NULL, 7, pinot[3], &tcb[3]);
    vTaskStartScheduler();
}
