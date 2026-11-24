/* NVIC: prioriteetit, sisäkkäiset keskeytykset, ketjutus ja BASEPRI.
 * Keskeytykset laukaistaan ohjelmallisesti, joten järjestys on joka
 * ajossa sama. */
#include <stdint.h>

#include "konsoli.h"
#include "mps2.h"

static volatile unsigned syvyys;   /* sisäkkäisyys tulosteen sisennykseen */
static volatile unsigned vaihe;    /* mitä käsittelijä tekee */

static void loki(unsigned irq, const char *mita) {
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr" : "=r"(ipsr));
    for (unsigned i = 0; i < syvyys; i++) {
        konsoli_kirjoita("  ");
    }
    tulosta("IRQ%u %s (prioriteetti %u, IPSR %u)\n", irq, mita,
            (unsigned)(NVIC->IPR[irq] >> 5), (unsigned)ipsr);
}

static int odottaa(unsigned irq) {
    return (NVIC->ISPR[irq / 32] >> (irq % 32)) & 1u;
}

// @alku kasittelijat
void VAPAA0_IRQHandler(void) {   /* IRQ13 */
    syvyys++;
    loki(13, "alkaa");
    if (vaihe == 2) {
        nvic_laukaise(VAPAA1_IRQn);   /* kiireellisempi: keskeyttää */
        muistiaita();
        nvic_laukaise(VAPAA2_IRQn);   /* vähemmän kiireinen: odottaa */
        muistiaita();
        tulosta("    IRQ15 odottaa: %s\n", odottaa(15) ? "kyllä" : "ei");
    }
    loki(13, "päättyy");
    syvyys--;
}

void VAPAA1_IRQHandler(void) {   /* IRQ14 */
    syvyys++;
    loki(14, "alkaa ja päättyy");
    syvyys--;
}

void VAPAA2_IRQHandler(void) {   /* IRQ15 */
    syvyys++;
    loki(15, "alkaa ja päättyy");
    syvyys--;
}
// @loppu kasittelijat

// @alku basepri
static void aseta_basepri(uint32_t arvo) {
    __asm__ volatile("msr basepri, %0\n\tisb" ::"r"(arvo) : "memory");
}
// @loppu basepri

int main(void) {
    konsoli_alusta();
    // @alku alustus
    nvic_prioriteetti(VAPAA0_IRQn, 2);
    nvic_prioriteetti(VAPAA1_IRQn, 1);
    nvic_prioriteetti(VAPAA2_IRQn, 3);
    nvic_salli(VAPAA0_IRQn);
    nvic_salli(VAPAA1_IRQn);
    nvic_salli(VAPAA2_IRQn);
    // @loppu alustus

    // @alku vaihe1
    tulosta("1) kolme keskeytystä odottaa yhtä aikaa\n");
    keskeytykset_pois();               /* PRIMASK = 1 */
    nvic_laukaise(VAPAA2_IRQn);
    nvic_laukaise(VAPAA0_IRQn);
    nvic_laukaise(VAPAA1_IRQn);
    tulosta("  ISPR = 0x%08x\n", (unsigned)NVIC->ISPR[0]);
    keskeytykset_paalle();             /* kaikki ajetaan tässä */
    // @loppu vaihe1

    // @alku vaihe2
    tulosta("2) käsittelijä laukaisee kaksi muuta\n");
    vaihe = 2;
    nvic_laukaise(VAPAA0_IRQn);
    muistiaita();
    vaihe = 0;
    // @loppu vaihe2

    // @alku vaihe3
    tulosta("3) sama prioriteetti ei keskeytä\n");
    nvic_prioriteetti(VAPAA1_IRQn, 2);
    vaihe = 2;
    nvic_laukaise(VAPAA0_IRQn);
    muistiaita();
    vaihe = 0;
    nvic_prioriteetti(VAPAA1_IRQn, 1);
    // @loppu vaihe3

    // @alku vaihe4
    tulosta("4) BASEPRI = 2: prioriteetit 2..7 peitetty\n");
    aseta_basepri(2u << 5);
    nvic_laukaise(VAPAA0_IRQn);        /* prioriteetti 2: odottaa */
    nvic_laukaise(VAPAA1_IRQn);        /* prioriteetti 1: ajetaan */
    muistiaita();
    tulosta("  IRQ13 odottaa: %s\n", odottaa(13) ? "kyllä" : "ei");
    aseta_basepri(0);                  /* 0 = ei peittoa */
    tulosta("  BASEPRI = 0\n");
    // @loppu vaihe4
    return 0;
}
