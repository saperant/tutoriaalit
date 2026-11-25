/* Prioriteetin inversio. Matala varaa väylän, korkea jää odottamaan
 * sitä, ja keskitason tehtävä, joka ei tarvitse väylää lainkaan,
 * viivästyttää korkeaa. Perusversio suojaa väylän binäärisemaforilla;
 * muunnelma 13-inversio-mutex (-DMUTEX) mutexilla, jonka haltija perii
 * odottajan prioriteetin. */
#include "aikajana.h"
#include "kide.h"
#include "konsoli.h"
#include "semihost.h"

static StaticSemaphore_t vayla_tila;
static SemaphoreHandle_t vayla;
static TaskHandle_t matala_kahva;

// @alku tehtavat
static void matala(void *parametri) {
    (void)parametri;
    xSemaphoreTake(vayla, portMAX_DELAY);
    tulosta("%3u matala varasi vaylan\n", xTaskGetTickCount());
    kide_kuormita(4);                  /* pitkä siirto väylällä */
    tulosta("%3u matala vapauttaa (prioriteetti nyt %u)\n",
            xTaskGetTickCount(), uxTaskPriorityGet(matala_kahva));
    xSemaphoreGive(vayla);
    tulosta("%3u matala valmis (prioriteetti %u)\n", xTaskGetTickCount(),
            uxTaskPriorityGet(matala_kahva));
    vTaskDelay(portMAX_DELAY);
}

static void keski(void *parametri) {
    (void)parametri;
    vTaskDelay(2);
    tulosta("%3u keski alkaa\n", xTaskGetTickCount());
    kide_kuormita(6);                  /* ei tarvitse väylää */
    tulosta("%3u keski valmis\n", xTaskGetTickCount());
    vTaskDelay(portMAX_DELAY);
}

static void korkea(void *parametri) {
    (void)parametri;
    vTaskDelay(1);
    TickType_t alku = xTaskGetTickCount();
    tulosta("%3u korkea tarvitsee vaylan\n", alku);
    xSemaphoreTake(vayla, portMAX_DELAY);
    tulosta("%3u korkea sai vaylan, odotti %u tikkia\n",
            xTaskGetTickCount(), xTaskGetTickCount() - alku);
    kide_kuormita(1);
    tulosta("%3u korkea vapauttaa\n", xTaskGetTickCount());
    xSemaphoreGive(vayla);
    vTaskDelay(portMAX_DELAY);
}
// @loppu tehtavat

// @alku luonti
static void luo_vayla(void) {
#ifdef MUTEX
    vayla = xSemaphoreCreateMutexStatic(&vayla_tila);
#else
    vayla = xSemaphoreCreateBinaryStatic(&vayla_tila);
    xSemaphoreGive(vayla);             /* binäärisemafori alkaa tyhjänä */
#endif
}
// @loppu luonti

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
    luo_vayla();
    TaskHandle_t k = xTaskCreateStatic(korkea, "korkea", 256, NULL, 3,
                                       pinot[0], &tcb[0]);
    TaskHandle_t m = xTaskCreateStatic(keski, "keski", 256, NULL, 2,
                                       pinot[1], &tcb[1]);
    matala_kahva = xTaskCreateStatic(matala, "matala", 256, NULL, 1,
                                     pinot[2], &tcb[2]);
    aikajana_lisaa(k);
    aikajana_lisaa(m);
    aikajana_lisaa(matala_kahva);
    aikajana_seuraa_prioriteettia(matala_kahva);
    xTaskCreateStatic(valvoja, "valvoja", 256, NULL, 7, pinot[3], &tcb[3]);
    vTaskStartScheduler();
}
