/* Kontekstinvaihto Cortex-M3:lla: uuden tehtävän alkukehys, tehtävän
 * ja keskeytyksen pinot (PSP ja MSP) sekä vuorottelu taskYIELDillä. */
#include <stdint.h>

#include "kide.h"
#include "konsoli.h"
#include "mps2.h"
#include "semihost.h"

static StaticTask_t ping_tcb, pong_tcb;
static StackType_t ping_pino[128], pong_pino[128];

static void ping_pong(void *parametri);

// @alku kehys
static void tulosta_kehys(TaskHandle_t t) {
    static const char *const nimet[16] = {  /* osoitteen mukaan */
        "r4", "r5", "r6", "r7", "r8", "r9", "r10", "r11",   /* PendSV */
        "r0", "r1", "r2", "r3", "r12", "lr", "pc", "xpsr"}; /* laitteisto */
    const StackType_t *sp = t->pino_osoitin;
    const StackType_t *huippu = t->pino_pohja + t->pino_sanat;
    tulosta("%s: kehys %u tavua pinon huipun alla\n", t->nimi,
            (unsigned)((huippu - sp) * 4));
    for (unsigned i = 0; i < 16; i++) {
        uint32_t arvo = sp[i];
        if (i == 8) {
            tulosta("  r0 = parametri \"%s\"\n",
                    (const char *)(uintptr_t)arvo);
        } else if (i == 13) {
            tulosta("  lr = kide_tehtava_palasi\n");
        } else if (i == 14) {
            tulosta("  pc = %s\n",
                    arvo == ((uint32_t)(uintptr_t)ping_pong & ~1u)
                        ? "ping_pong" : "?");
        } else {
            tulosta("  %s = %08x\n", nimet[i], (unsigned)arvo);
        }
    }
}
// @loppu kehys

// @alku rekisterit
static uint32_t lue_control(void) {
    uint32_t arvo;
    __asm__ volatile("mrs %0, control" : "=r"(arvo));
    return arvo;
}

static uint32_t lue_sp(void) {
    uint32_t arvo;
    __asm__ volatile("mov %0, sp" : "=r"(arvo));
    return arvo;
}

static uint32_t lue_psp(void) {
    uint32_t arvo;
    __asm__ volatile("mrs %0, psp" : "=r"(arvo));
    return arvo;
}

static uint32_t lue_msp(void) {
    uint32_t arvo;
    __asm__ volatile("mrs %0, msp" : "=r"(arvo));
    return arvo;
}

static uint32_t lue_ipsr(void) {
    uint32_t arvo;
    __asm__ volatile("mrs %0, ipsr" : "=r"(arvo));
    return arvo;
}

static void kerro_tila(const char *missa) {
    uint32_t sp = lue_sp();
    tulosta("%s: IPSR=%u CONTROL=%u pino=%s\n", missa, (unsigned)lue_ipsr(),
            (unsigned)lue_control(),
            sp == lue_psp() ? "PSP" : sp == lue_msp() ? "MSP" : "?");
}

__attribute__((noinline)) void VAPAA0_IRQHandler(void) {
    uint32_t exc_return = (uint32_t)(uintptr_t)__builtin_return_address(0);
    kerro_tila("keskeytys");
    tulosta("keskeytys: EXC_RETURN=%08x\n", (unsigned)exc_return);
}
// @loppu rekisterit

// @alku vuorottelu
static void ping_pong(void *parametri) {
    const char *sana = parametri;
    if (xTaskGetCurrentTaskHandle() == &ping_tcb) {
        kerro_tila("tehtava");
        nvic_prioriteetti(VAPAA0_IRQn, 6);
        nvic_salli(VAPAA0_IRQn);
        nvic_laukaise(VAPAA0_IRQn);
        muistiaita();
    }
    for (unsigned i = 0; i < 3; i++) {
        tulosta("%s %u\n", sana, i);
        taskYIELD();   /* sama prioriteetti: toinen pääsee vuoroon */
    }
    tulosta("%s: valittu %u kertaa\n", sana,
            (unsigned)xTaskGetCurrentTaskHandle()->vaihdot);
    if (xTaskGetCurrentTaskHandle() == &pong_tcb) {
        lopeta(0);
    }
    vTaskDelay(portMAX_DELAY);
}
// @loppu vuorottelu

int main(void) {
    konsoli_alusta();
    kerro_tila("main");
    TaskHandle_t ping = xTaskCreateStatic(ping_pong, "ping", 128, "ping",
                                          2, ping_pino, &ping_tcb);
    xTaskCreateStatic(ping_pong, "pong", 128, "pong", 2, pong_pino,
                      &pong_tcb);
    tulosta_kehys(ping);
    vTaskStartScheduler();
}
