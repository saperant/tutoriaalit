/* Cortex-M3:n tilat ja pinot: CPUID, CONTROL, IPSR, EXC_RETURN,
 * poikkeuskehys ja siirtyminen prosessipinoon (PSP). */
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

// @alku svc
/* SVC_Handler on assemblyä, koska C-funktion alku muuttaisi LR:n ja
 * pinon ennen kuin ehdimme lukea ne. Bitti 2 EXC_RETURN-arvossa kertoo,
 * kumpaan pinoon kehys tallennettiin. */
__attribute__((naked)) void SVC_Handler(void) {
    __asm__ volatile(
        "tst   lr, #4\n\t"
        "ite   eq\n\t"
        "mrseq r0, msp\n\t"
        "mrsne r0, psp\n\t"
        "mov   r1, lr\n\t"
        "b     svc_kasittely\n\t");
}

/* Kehys: r0, r1, r2, r3, r12, lr, pc, xpsr. */
void svc_kasittely(uint32_t *kehys, uint32_t exc_return) {
    uint16_t kasky = *(const uint16_t *)(kehys[6] - 2);
    uint32_t numero = kasky & 0xFFu;   /* svc #n: n käskyn alatavussa */
    tila("  SVC");
    tulosta("  SVC #%u, EXC_RETURN=0x%08x, kehys %s-pinossa\n",
            (unsigned)numero, (unsigned)exc_return,
            (exc_return & 4u) ? "PSP" : "MSP");
    if (numero == 1) {
        tulosta("  kehys: r0=%u r1=%u r2=%u r3=%u, xPSR.T=%u\n",
                (unsigned)kehys[0], (unsigned)kehys[1],
                (unsigned)kehys[2], (unsigned)kehys[3],
                (unsigned)((kehys[7] >> 24) & 1u));
        kehys[0] = kehys[0] + kehys[1];   /* paluuarvo kutsujan r0:aan */
    } else if (numero == 2) {
        uint32_t control;
        __asm__ volatile("mrs %0, control" : "=r"(control));
        __asm__ volatile("msr control, %0\n\tisb"
                         ::"r"(control & ~1u) : "memory");
    }
}
// @loppu svc

// @alku kutsu
static uint32_t summa_svc(uint32_t a, uint32_t b) {
    register uint32_t r0 __asm__("r0") = a;
    register uint32_t r1 __asm__("r1") = b;
    register uint32_t r2 __asm__("r2") = 30;
    register uint32_t r3 __asm__("r3") = 40;
    __asm__ volatile("svc #1"
                     : "+r"(r0)
                     : "r"(r1), "r"(r2), "r"(r3)
                     : "memory");
    return r0;
}
// @loppu kutsu

// @alku psp
/* Kutsuu funktiota prosessipinossa ja palaa sitten pääpinoon. Pinoa
 * ei voi vaihtaa kesken C-funktion, koska kääntäjä tallentaa paluu-
 * osoitteen ja rekisterit pinoon funktion alussa ja hakee ne lopussa. */
void aja_psp(void (*funktio)(void), uint64_t *huippu);
/* AAPCS: ensimmäinen argumentti on r0:ssa, toinen r1:ssä. */
__asm__(".text\n"
        ".global aja_psp\n"
        ".type aja_psp, %function\n"
        ".thumb_func\n"
        "aja_psp:\n"
        "    msr   psp, r1\n"
        "    movs  r1, #2\n"         /* CONTROL.SPSEL = 1 */
        "    msr   control, r1\n"
        "    isb\n"
        "    push  {r4, lr}\n"       /* nyt jo PSP-pinoon */
        "    blx   r0\n"
        "    pop   {r4, lr}\n"
        "    movs  r1, #0\n"         /* takaisin MSP:hen */
        "    msr   control, r1\n"
        "    isb\n"
        "    bx    lr\n");
// @loppu psp

// @alku prosessi
static void prosessi(void) {
    tila("prosessi");
    tulosta("summa_svc(1, 2) = %u\n", (unsigned)summa_svc(1, 2));

    /* Etuoikeuksista luopuminen: CONTROL.nPRIV = 1. */
    __asm__ volatile("msr control, %0\n\tisb" ::"r"(3u) : "memory");
    tila("prosessi");
    __asm__ volatile("msr control, %0\n\tisb" ::"r"(2u) : "memory");
    tulosta("yritys palauttaa etuoikeus: CONTROL=%u\n",
            (unsigned)lue_control());
    __asm__ volatile("svc #2" ::: "memory");   /* käyttöjärjestelmältä */
    tila("prosessi");
}
// @loppu prosessi

static uint64_t prosessipino[128];   /* 1 KiB, 8 tavun tasaus */

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

    // @alku main
    tila("main");
    tulosta("summa_svc(10, 20) = %u\n", (unsigned)summa_svc(10, 20));
    aja_psp(prosessi, &prosessipino[128]);
    tila("main");
    // @loppu main
    return 0;
}
