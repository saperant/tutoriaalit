/* Tapahtumaryhmä: sovellus odottaa, että kolme alijärjestelmää on
 * käynnistynyt (kaikki bitit), ja hälytystehtävä odottaa kumpaa
 * tahansa kahdesta hälytyksestä (mikä tahansa bitti). */
#include "kide.h"
#include "konsoli.h"
#include "semihost.h"

// @alku bitit
#define VERKKO_VALMIS    (1u << 0)
#define ANTURI_VALMIS    (1u << 1)
#define TALLENNUS_VALMIS (1u << 2)
#define KAIKKI_VALMIINA  (VERKKO_VALMIS | ANTURI_VALMIS | TALLENNUS_VALMIS)
#define YLILAMPO         (1u << 8)
#define PAINIKE          (1u << 9)
// @loppu bitit

static StaticEventGroup_t ryhma_tila;
static EventGroupHandle_t ryhma;

typedef struct {
    TickType_t kesto;
    EventBits_t bitti;
} kaynnistys_t;

// @alku alijarjestelma
static void alijarjestelma(void *parametri) {
    const kaynnistys_t *k = parametri;
    kide_kuormita(k->kesto);   /* alustus vie aikaa */
    tulosta("%3u %s valmis\n", xTaskGetTickCount(),
            pcTaskGetName(xTaskGetCurrentTaskHandle()));
    xEventGroupSetBits(ryhma, k->bitti);
    vTaskDelay(portMAX_DELAY);
}
// @loppu alijarjestelma

// @alku sovellus
static void sovellus(void *parametri) {
    (void)parametri;
    EventBits_t bitit = xEventGroupWaitBits(ryhma, KAIKKI_VALMIINA,
                                            pdFALSE, pdTRUE, 20);
    if ((bitit & KAIKKI_VALMIINA) != KAIKKI_VALMIINA) {
        tulosta("%3u sovellus: kaynnistys aikakatkaistiin\n",
                xTaskGetTickCount());
        lopeta(1);
    }
    tulosta("%3u sovellus kaynnistyy (bitit %03x)\n", xTaskGetTickCount(),
            (unsigned)bitit);
    vTaskDelay(3);
    xEventGroupSetBits(ryhma, PAINIKE);
    vTaskDelay(4);
    xEventGroupSetBits(ryhma, YLILAMPO | PAINIKE);
    vTaskDelay(portMAX_DELAY);
}
// @loppu sovellus

// @alku halytys
static void halytys(void *parametri) {
    (void)parametri;
    for (unsigned kerta = 0; kerta < 3; kerta++) {
        /* Mikä tahansa hälytysbitti; luetut bitit nollataan. */
        EventBits_t bitit = xEventGroupWaitBits(ryhma, YLILAMPO | PAINIKE,
                                                pdTRUE, pdFALSE, 10);
        if ((bitit & (YLILAMPO | PAINIKE)) == 0) {
            tulosta("%3u halytys: ei halytyksia 10 tikkiin\n",
                    xTaskGetTickCount());
            continue;
        }
        tulosta("%3u halytys:%s%s\n", xTaskGetTickCount(),
                bitit & YLILAMPO ? " ylilampo" : "",
                bitit & PAINIKE ? " painike" : "");
    }
    tulosta("%3u ryhman bitit nyt %03x\n", xTaskGetTickCount(),
            (unsigned)xEventGroupGetBits(ryhma));
    lopeta(0);
}
// @loppu halytys

static const kaynnistys_t verkko = {3, VERKKO_VALMIS};
static const kaynnistys_t anturi = {5, ANTURI_VALMIS};
static const kaynnistys_t tallennus = {2, TALLENNUS_VALMIS};

static StaticTask_t tcb[5];
static StackType_t pinot[5][256];

int main(void) {
    konsoli_alusta();
    ryhma = xEventGroupCreateStatic(&ryhma_tila);
    xTaskCreateStatic(alijarjestelma, "verkko", 256, (void *)&verkko, 1,
                      pinot[0], &tcb[0]);
    xTaskCreateStatic(alijarjestelma, "anturi", 256, (void *)&anturi, 1,
                      pinot[1], &tcb[1]);
    xTaskCreateStatic(alijarjestelma, "tallennus", 256, (void *)&tallennus,
                      1, pinot[2], &tcb[2]);
    xTaskCreateStatic(sovellus, "sovellus", 256, NULL, 3, pinot[3],
                      &tcb[3]);
    xTaskCreateStatic(halytys, "halytys", 256, NULL, 4, pinot[4], &tcb[4]);
    vTaskStartScheduler();
}
