/* Kriittinen osio ja keskeytysprioriteetit: BASEPRI peittää vain ne
 * keskeytykset, joiden prioriteetti on configMAX_SYSCALL_INTERRUPT_
 * PRIORITY tai heikompi. Kiireellisempi keskeytys ajetaan heti, mutta se
 * ei saa kutsua ytimen funktioita. Lopuksi ohjelma rikkoo säännön, ja
 * ytimen väite pysäyttää sen. */
#include "kide.h"
#include "konsoli.h"
#include "mps2.h"
#include "semihost.h"

#define NOPEA_IRQn  VAPAA1_IRQn   /* prioriteetti 2: ydin ei peitä */
#define HIDAS_IRQn  VAPAA2_IRQn   /* prioriteetti 6: saa kutsua FromISR */

static StaticSemaphore_t merkki_tila;
static SemaphoreHandle_t merkki;
static volatile BaseType_t riko_saanto;

// @alku kasittelijat
void VAPAA1_IRQHandler(void) {
    tulosta("  nopea keskeytys (prioriteetti 2) ajetaan heti\n");
    if (riko_saanto) {
        BaseType_t heratti = pdFALSE;
        xSemaphoreGiveFromISR(merkki, &heratti);   /* VIRHE */
    }
}

void VAPAA2_IRQHandler(void) {
    BaseType_t heratti = pdFALSE;
    tulosta("  hidas keskeytys (prioriteetti 6) antaa semaforin\n");
    xSemaphoreGiveFromISR(merkki, &heratti);
    portYIELD_FROM_ISR(heratti);
}
// @loppu kasittelijat

static int odottaa(unsigned irq) {
    return (NVIC->ISPR[irq / 32] >> (irq % 32)) & 1u;
}

// @alku tehtava
static void tehtava(void *parametri) {
    (void)parametri;
    nvic_prioriteetti(NOPEA_IRQn, 2);
    nvic_prioriteetti(HIDAS_IRQn, 6);
    nvic_salli(NOPEA_IRQn);
    nvic_salli(HIDAS_IRQn);

    tulosta("kriittinen osio alkaa\n");
    taskENTER_CRITICAL();
    nvic_laukaise(HIDAS_IRQn);
    nvic_laukaise(NOPEA_IRQn);
    muistiaita();
    tulosta("  hidas odottaa: %s\n", odottaa(HIDAS_IRQn) ? "kylla" : "ei");
    tulosta("kriittinen osio paattyy\n");
    taskEXIT_CRITICAL();             /* hidas keskeytys ajetaan tässä */

    if (xSemaphoreTake(merkki, 0) == pdPASS) {
        tulosta("tehtava sai semaforin\n");
    }
    tulosta("nopea keskeytys kutsuu ydinta:\n");
    riko_saanto = pdTRUE;
    nvic_laukaise(NOPEA_IRQn);
    muistiaita();
    tulosta("tanne ei paasta\n");
    lopeta(0);
}
// @loppu tehtava

static StaticTask_t tcb;
static StackType_t pino[256];

int main(void) {
    konsoli_alusta();
    merkki = xSemaphoreCreateBinaryStatic(&merkki_tila);
    xTaskCreateStatic(tehtava, "tehtava", 256, NULL, 1, pino, &tcb);
    vTaskStartScheduler();
}
