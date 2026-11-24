/* Sarjaportin komentotulkki: UART0:n vastaanottokeskeytys lähettää
 * tavut jonoon, ja komentotehtävä kokoaa niistä rivejä. Tehtävä nukkuu
 * jonossa, kun syötettä ei ole: idle-tehtävä ajaa WFI:tä. */
#include <string.h>

#include "kide.h"
#include "konsoli.h"
#include "mps2.h"
#include "semihost.h"

#define TAVUJONO 96u
static uint8_t tavujen_muisti[TAVUJONO];
static StaticQueue_t tavujen_tila;
static QueueHandle_t tavut;
static volatile uint32_t hukatut;

static StaticTask_t komento_tcb, vahti_tcb;
static StackType_t komento_pino[256], vahti_pino[128];

// @alku isr
void UART0RX_IRQHandler(void) {
    BaseType_t heratti = pdFALSE;
    UART0->INTSTATUS = UART_INT_RX;   /* kuittaus ensin (ks. mikro-
                                         kontrollerit, luku 7) */
    while (UART0->STATE & UART_STATE_RXFULL) {
        uint8_t tavu = (uint8_t)UART0->DATA;
        if (xQueueSendFromISR(tavut, &tavu, &heratti) != pdPASS) {
            hukatut++;   /* jono täynnä: keskeytys ei voi odottaa */
        }
    }
    portYIELD_FROM_ISR(heratti);
}
// @loppu isr

// @alku komennot
static void tehtavat(void) {
    TaskHandle_t lista[] = {&komento_tcb, &vahti_tcb};
    for (unsigned i = 0; i < 2; i++) {
        /* Pinon vesiraja riippuisi siitä, missä kohdassa UART-
         * keskeytykset osuivat tehtävään, joten sitä ei tulosteta. */
        tulosta("  %s: prioriteetti %u, pino %u sanaa\n",
                pcTaskGetName(lista[i]), uxTaskPriorityGet(lista[i]),
                (unsigned)lista[i]->pino_sanat);
    }
}

static BaseType_t suorita(const char *rivi) {
    if (strcmp(rivi, "tehtavat") == 0) {
        tehtavat();
    } else if (strncmp(rivi, "kaiku ", 6) == 0) {
        tulosta("  %s\n", rivi + 6);
    } else if (strcmp(rivi, "hukatut") == 0) {
        tulosta("  hukattu %u tavua\n", (unsigned)hukatut);
    } else if (strcmp(rivi, "lopeta") == 0) {
        return pdFALSE;
    } else {
        tulosta("  tuntematon komento '%s'\n", rivi);
    }
    return pdTRUE;
}
// @loppu komennot

// @alku komento
static void komentotulkki(void *parametri) {
    (void)parametri;
    UART0->CTRL |= UART_CTRL_RXINTEN;
    nvic_prioriteetti(UART0RX_IRQn, 6);
    nvic_salli(UART0RX_IRQn);
    nvic_laukaise(UART0RX_IRQn);   /* ennen sallintaa tulleet tavut */

    char rivi[40];
    size_t pituus = 0;
    for (;;) {
        uint8_t tavu;
        xQueueReceive(tavut, &tavu, portMAX_DELAY);
        if (tavu == '\r') {
            continue;
        }
        if (tavu != '\n') {
            if (pituus < sizeof rivi - 1) {
                rivi[pituus++] = (char)tavu;
            }
            continue;
        }
        rivi[pituus] = '\0';
        pituus = 0;
        tulosta("> %s\n", rivi);
        if (!suorita(rivi)) {
            lopeta(0);
        }
    }
}
// @loppu komento

/* Matalan prioriteetin tehtävä, joka kuluttaa vähän pinoa. */
static void vahti(void *parametri) {
    (void)parametri;
    for (;;) {
        vTaskDelay(1000);
    }
}

int main(void) {
    konsoli_alusta();
    tavut = xQueueCreateStatic(TAVUJONO, 1, tavujen_muisti, &tavujen_tila);
    xTaskCreateStatic(komentotulkki, "komento", 256, NULL, 2, komento_pino,
                      &komento_tcb);
    xTaskCreateStatic(vahti, "vahti", 128, NULL, 1, vahti_pino, &vahti_tcb);
    vTaskStartScheduler();
}
