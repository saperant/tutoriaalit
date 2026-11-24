/* Ensimmäinen Kide-ohjelma: kaksi jaksollista tehtävää ja valvoja,
 * joka lopettaa ajon. Sama ohjelma ajetaan QEMU:ssa ja isäntä-
 * koneella. */
#include "kide.h"
#include "konsoli.h"
#include "semihost.h"

// @alku tehtavat
static void mittaus(void *parametri) {
    (void)parametri;
    for (;;) {
        tulosta("%3u mittaus\n", xTaskGetTickCount());
        vTaskDelay(10);
    }
}

static void raportti(void *parametri) {
    (void)parametri;
    for (;;) {
        tulosta("%3u raportti\n", xTaskGetTickCount());
        vTaskDelay(25);
    }
}

static void valvoja(void *parametri) {
    (void)parametri;
    vTaskDelay(60);
    tulosta("%3u valvoja lopettaa\n", xTaskGetTickCount());
    lopeta(0);
}
// @loppu tehtavat

// @alku main
static StaticTask_t mittaus_tcb, raportti_tcb, valvoja_tcb;
static StackType_t mittaus_pino[256], raportti_pino[256], valvoja_pino[256];

int main(void) {
    konsoli_alusta();
    xTaskCreateStatic(mittaus, "mittaus", 256, NULL, 2, mittaus_pino,
                      &mittaus_tcb);
    xTaskCreateStatic(raportti, "raportti", 256, NULL, 1, raportti_pino,
                      &raportti_tcb);
    xTaskCreateStatic(valvoja, "valvoja", 256, NULL, 3, valvoja_pino,
                      &valvoja_tcb);
    vTaskStartScheduler();   /* ei palaa */
}
// @loppu main
