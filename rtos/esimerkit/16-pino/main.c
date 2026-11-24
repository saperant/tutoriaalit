/* Pinon mitoitus ja ylivuoto: vesiraja kertoo, paljonko pinoa on jäänyt
 * koskematta. Lopuksi rekursiivinen tehtävä vuotaa pinonsa yli, ja ydin
 * huomaa sen seuraavassa tehtävänvaihdossa vartija-arvoista. */
#include <string.h>

#include "kide.h"
#include "konsoli.h"
#include "semihost.h"

// @alku kuormat
static void kevyt(void *parametri) {
    (void)parametri;
    for (;;) {
        vTaskDelay(5);
    }
}

static __attribute__((noinline)) uint32_t summaa(const uint8_t *data) {
    uint32_t summa = 0;
    for (unsigned i = 0; i < 256; i++) {
        summa += data[i];
    }
    return summa;
}

static void raskas(void *parametri) {
    (void)parametri;
    for (;;) {
        uint8_t puskuri[256];          /* 64 sanaa pinossa */
        memset(puskuri, 1, sizeof puskuri);
        if (summaa(puskuri) != 256) {
            lopeta(1);
        }
        vTaskDelay(5);
    }
}
// @loppu kuormat

// @alku rekursio
/* Pino ja sen alla suoja-alue samassa rakenteessa: ylivuoto osuu
 * suoja-alueeseen eikä muihin muuttujiin. Oikeassa laitteessa suoja-
 * alue olisi MPU:n kieltämä, ja ylivuoto pysähtyisi heti vikaan. */
static struct {
    StackType_t suoja[64];
    StackType_t pino[64];
} rekursion_muisti;

static __attribute__((noinline)) uint32_t syvenna(unsigned taso) {
    volatile uint32_t paikallinen[8];   /* 32 tavua joka tasolla */
    for (unsigned i = 0; i < 8; i++) {
        paikallinen[i] = taso + i;
    }
    return taso == 0 ? paikallinen[0] : syvenna(taso - 1) + paikallinen[7];
}

static void rekursio(void *parametri) {
    unsigned syvyys = (unsigned)(uintptr_t)parametri;
    tulosta("rekursio %u tasoa\n", syvyys);
    volatile uint32_t tulos = syvenna(syvyys);
    (void)tulos;
    vTaskDelay(1);                       /* tarkistus tehtävänvaihdossa */
    tulosta("rekursio selvisi\n");
    vTaskDelay(portMAX_DELAY);
}

void vApplicationStackOverflowHook(TaskHandle_t tehtava, const char *nimi) {
    (void)tehtava;
    unsigned alin = 64;   /* alin suoja-alueen sana, johon kirjoitettiin */
    for (unsigned i = 64; i > 0; i--) {
        if (rekursion_muisti.suoja[i - 1] != 0xA5A5A5A5u) {
            alin = i - 1;
        }
    }
    tulosta("PINON YLIVUOTO: %s, %u sanaa pinon alapuolelle\n", nimi,
            64 - alin);
    lopeta(97);
}
// @loppu rekursio

static StaticTask_t tcb[4];
static StackType_t kevyt_pino[128], raskas_pino[128], valvoja_pino[256];

// @alku valvoja
static void valvoja(void *parametri) {
    (void)parametri;
    vTaskDelay(10);
    TaskHandle_t tehtavat[] = {&tcb[0], &tcb[1]};
    for (unsigned i = 0; i < 2; i++) {
        tulosta("%s: pinoa %u sanaa, koskematta %u\n",
                pcTaskGetName(tehtavat[i]), (unsigned)tehtavat[i]->pino_sanat,
                uxTaskGetStackHighWaterMark(tehtavat[i]));
    }
    xTaskCreateStatic(rekursio, "rekursio", 64, (void *)8u,
                      3, rekursion_muisti.pino, &tcb[3]);
    vTaskDelay(portMAX_DELAY);
}
// @loppu valvoja

int main(void) {
    konsoli_alusta();
    for (unsigned i = 0; i < 64; i++) {
        rekursion_muisti.suoja[i] = 0xA5A5A5A5u;
    }
    xTaskCreateStatic(kevyt, "kevyt", 128, NULL, 1, kevyt_pino, &tcb[0]);
    xTaskCreateStatic(raskas, "raskas", 128, NULL, 1, raskas_pino, &tcb[1]);
    xTaskCreateStatic(valvoja, "valvoja", 256, NULL, 2, valvoja_pino,
                      &tcb[2]);
    vTaskStartScheduler();
}
