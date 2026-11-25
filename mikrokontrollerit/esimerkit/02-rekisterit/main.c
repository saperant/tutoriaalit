/* Cortex-M3:n rekisterit ja tilat: CPUID, vektoritaulun alku,
 * CONTROL ja IPSR. */
#include <stdint.h>

#include "konsoli.h"
#include "mps2.h"

// @alku erikoisrekisterit
static uint32_t lue_control(void) {
    uint32_t arvo;
    __asm__ volatile("mrs %0, control" : "=r"(arvo));
    return arvo;
}
static uint32_t lue_ipsr(void) {
    uint32_t arvo;
    __asm__ volatile("mrs %0, ipsr" : "=r"(arvo));
    return arvo;
}
static void tila(const char *missa) {
    uint32_t control = lue_control();
    uint32_t ipsr = lue_ipsr();
    tulosta("%s: IPSR=%u (%s), CONTROL=%u: %s, %s\n", missa,
            (unsigned)ipsr, ipsr == 0 ? "Thread" : "Handler",
            (unsigned)control,
            (ipsr == 0 && (control & 1u)) ? "ei-etuoikeutettu"
                                          : "etuoikeutettu",
            (ipsr == 0 && (control & 2u)) ? "PSP" : "MSP");
}
// @loppu erikoisrekisterit

int main(void) {
    konsoli_alusta();
    // @alku cpuid
    uint32_t cpuid = SCB->CPUID;
    tulosta("CPUID 0x%08x: valmistaja 0x%x, osa 0x%x, r%up%u\n",
            (unsigned)cpuid, (unsigned)(cpuid >> 24),
            (unsigned)((cpuid >> 4) & 0xFFFu),
            (unsigned)((cpuid >> 20) & 0xFu), (unsigned)(cpuid & 0xFu));
    /* Vektoritaulu on resetin jälkeen osoitteessa 0 (VTOR = 0). */
    const uint32_t *vektorit = (const uint32_t *)SCB->VTOR;
    tulosta("vektori 0 (MSP:n alkuarvo) 0x%08x\n", (unsigned)vektorit[0]);
    tulosta("vektori 1 (Reset_Handler) pariton: %s\n",
            (vektorit[1] & 1u) ? "kyllä, Thumb" : "ei");
    // @loppu cpuid
    tila("main");
    return 0;
}
