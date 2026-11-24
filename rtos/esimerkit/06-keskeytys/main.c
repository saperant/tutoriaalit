/* Viivästetty keskeytyskäsittely: käsittelijä tekee vain välttämättömän
 * ja herättää tehtävän semaforilla. Kahdella ensimmäisellä kerralla
 * käsittelijä pyytää vaihtoa (portYIELD_FROM_ISR), kahdella viimeisellä
 * ei, jolloin tehtävä pääsee ajoon vasta seuraavassa tikissä. */
#include "kide.h"
#include "konsoli.h"
#include "mps2.h"
#include "semihost.h"

#define ANTURI_IRQn VAPAA0_IRQn

static StaticSemaphore_t valmis_tila;
static SemaphoreHandle_t valmis;
static volatile uint32_t nayte;          /* "laitteen datarekisteri" */
static volatile TickType_t keskeytyshetki;
static volatile BaseType_t pyyda_vaihto;

// @alku isr
void VAPAA0_IRQHandler(void) {
    BaseType_t heratti = pdFALSE;
    keskeytyshetki = xTaskGetTickCount();
    tulosta("%3u   ISR: naytteen %u kuittaus\n", keskeytyshetki,
            (unsigned)nayte);
    xSemaphoreGiveFromISR(valmis, &heratti);
    if (pyyda_vaihto) {
        portYIELD_FROM_ISR(heratti);   /* vaihto heti käsittelijän jälkeen */
    }
}
// @loppu isr

// @alku kasittelija
static void kasittelija(void *parametri) {
    (void)parametri;
    for (;;) {
        xSemaphoreTake(valmis, portMAX_DELAY);
        TickType_t nyt = xTaskGetTickCount();
        tulosta("%3u   kasittelija: nayte %u, viive %u tikkia\n", nyt,
                (unsigned)nayte, nyt - keskeytyshetki);
    }
}
// @loppu kasittelija

// @alku laukaisija
static void laukaisija(void *parametri) {
    (void)parametri;
    nvic_prioriteetti(ANTURI_IRQn, 6);   /* heikompi kuin MAX_SYSCALL (5) */
    nvic_salli(ANTURI_IRQn);
    TickType_t herays = 0;
    for (uint32_t n = 1; n <= 4; n++) {
        vTaskDelayUntil(&herays, 5);
        pyyda_vaihto = n <= 2;
        nayte = n;
        tulosta("%3u laukaisija: keskeytys %u (%s)\n", xTaskGetTickCount(),
                (unsigned)n, pyyda_vaihto ? "vaihto heti" : "ei vaihtoa");
        nvic_laukaise(ANTURI_IRQn);   /* kuin laite olisi valmis */
        muistiaita();
        tulosta("%3u laukaisija jatkaa\n", xTaskGetTickCount());
        kide_kuormita(2);
    }
    lopeta(0);
}
// @loppu laukaisija

static StaticTask_t tcb[2];
static StackType_t pinot[2][256];

int main(void) {
    konsoli_alusta();
    valmis = xSemaphoreCreateBinaryStatic(&valmis_tila);
    xTaskCreateStatic(kasittelija, "kasittelija", 256, NULL, 3, pinot[0],
                      &tcb[0]);
    xTaskCreateStatic(laukaisija, "laukaisija", 256, NULL, 1, pinot[1],
                      &tcb[1]);
    vTaskStartScheduler();
}
