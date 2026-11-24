/* Etuoikeutus: tärkeämpi tehtävä keskeyttää vähemmän tärkeän heti,
 * kun se tulee valmiiksi. Aikajana näyttää, kuka ajoi milloinkin. */
#include "aikajana.h"
#include "kide.h"
#include "konsoli.h"
#include "semihost.h"

// @alku tehtava
typedef struct {
    TickType_t herays;   /* milloin tehtävä tulee valmiiksi */
    TickType_t tyo;      /* laskentaa tikkeinä */
} kuorma_t;

static void tyontekija(void *parametri) {
    const kuorma_t *kuorma = parametri;
    const char *nimi = pcTaskGetName(xTaskGetCurrentTaskHandle());
    vTaskDelay(kuorma->herays);
    tulosta("%3u %s alkaa\n", xTaskGetTickCount(), nimi);
    kide_kuormita(kuorma->tyo);
    tulosta("%3u %s valmis\n", xTaskGetTickCount(), nimi);
    vTaskDelay(portMAX_DELAY);   /* ei palaa: odottaa ikuisesti */
}
// @loppu tehtava

static const kuorma_t matala_kuorma = {0, 6};
static const kuorma_t keski_kuorma = {2, 3};
static const kuorma_t korkea_kuorma = {3, 1};

static StaticTask_t tcb[4];
static StackType_t pinot[4][256];

static void valvoja(void *parametri) {
    (void)parametri;
    vTaskDelay(12);
    tulosta("\n");
    aikajana_tulosta(12);
    tulosta("\n");
    aikajana_tilastot();
    lopeta(0);
}

int main(void) {
    konsoli_alusta();
    static TaskHandle_t tehtavat[3];
    tehtavat[0] = xTaskCreateStatic(tyontekija, "matala", 256,
                                    (void *)&matala_kuorma, 1, pinot[0],
                                    &tcb[0]);
    tehtavat[1] = xTaskCreateStatic(tyontekija, "keski", 256,
                                    (void *)&keski_kuorma, 2, pinot[1],
                                    &tcb[1]);
    tehtavat[2] = xTaskCreateStatic(tyontekija, "korkea", 256,
                                    (void *)&korkea_kuorma, 3, pinot[2],
                                    &tcb[2]);
    for (unsigned i = 0; i < 3; i++) {
        aikajana_lisaa(tehtavat[2 - i]);
    }
    xTaskCreateStatic(valvoja, "valvoja", 256, NULL, 7, pinot[3],
                      &tcb[3]);
    vTaskStartScheduler();
}
