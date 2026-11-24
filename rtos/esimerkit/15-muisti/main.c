/* Muisti RTOSissa: tehtävät luodaan dynaamisesti heap_1-keosta
 * käynnistyksessä, ja viestit kulkevat kiinteän kokoisista lohkoista
 * koostuvan poolin kautta. Jonossa kulkee vain osoitin, joten viestiä
 * ei kopioida (zero copy). */
#include <string.h>

#include "kide.h"
#include "konsoli.h"
#include "pooli.h"
#include "semihost.h"

// @alku viesti
typedef struct {
    uint32_t numero;
    char teksti[20];
} viesti_t;

#define LOHKOJA 3u
static uint64_t poolin_muisti[LOHKOJA * sizeof(viesti_t) / 8u + 1u];
static pooli_t pooli;

static uint8_t jonon_muisti[8 * sizeof(viesti_t *)];
static StaticQueue_t jonon_tila;
static QueueHandle_t jono;       /* alkiona osoitin lohkoon */
// @loppu viesti

// @alku tuottaja
static void tuottaja(void *parametri) {
    (void)parametri;
    for (uint32_t n = 1; n <= 5; n++) {
        viesti_t *v = pooli_varaa(&pooli, 10);
        if (v == NULL) {
            tulosta("%3u tuottaja: pooli tyhja\n", xTaskGetTickCount());
            continue;
        }
        v->numero = n;
        strcpy(v->teksti, n % 2 ? "mittaus" : "tila");
        xQueueSend(jono, &v, portMAX_DELAY);   /* lähetetään osoitin */
        tulosta("%3u tuottaja: viesti %u, lohkoja vapaana %u\n",
                xTaskGetTickCount(), n, (unsigned)pooli_vapaana(&pooli));
    }
    vTaskDelay(portMAX_DELAY);
}
// @loppu tuottaja

// @alku kuluttaja
static void kuluttaja(void *parametri) {
    (void)parametri;
    viesti_t *v;
    while (xQueueReceive(jono, &v, 10) == pdPASS) {
        kide_kuormita(2);
        tulosta("%3u kuluttaja: %u %s\n", xTaskGetTickCount(), v->numero,
                v->teksti);
        pooli_vapauta(&pooli, v);      /* omistus palaa poolille */
    }
    tulosta("%3u valmis, lohkoja vapaana %u, keosta vapaana %u tavua\n",
            xTaskGetTickCount(), (unsigned)pooli_vapaana(&pooli),
            (unsigned)xPortGetFreeHeapSize());
    lopeta(0);
}
// @loppu kuluttaja

// @alku main
int main(void) {
    konsoli_alusta();
    pooli_alusta(&pooli, poolin_muisti, 24, LOHKOJA);
    jono = xQueueCreateStatic(8, sizeof(viesti_t *), jonon_muisti,
                              &jonon_tila);
    size_t alussa = xPortGetFreeHeapSize();
    if (xTaskCreate(tuottaja, "tuottaja", 128, NULL, 2, NULL) != pdPASS ||
        xTaskCreate(kuluttaja, "kuluttaja", 128, NULL, 1, NULL) != pdPASS) {
        tulosta("keko loppui\n");
        return 1;
    }
    tulosta("keko: %u tavua, kaksi tehtavaa vei %u (TCB %u + pino %u)\n",
            (unsigned)alussa, (unsigned)(alussa - xPortGetFreeHeapSize()),
            (unsigned)sizeof(StaticTask_t), 128u * 4u);
    vTaskStartScheduler();
}
// @loppu main
