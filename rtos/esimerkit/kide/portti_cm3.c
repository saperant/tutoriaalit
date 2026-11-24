/* Cortex-M3-portti: pinon alustus, käynnistys, PendSV ja SysTick.
 *
 * Tehtävät ajetaan Thread-tilassa prosessipinolla (PSP). Keskeytykset
 * ja ydin käyttävät pääpinoa (MSP). Kriittinen osio nostaa BASEPRI:n
 * arvoon configMAX_SYSCALL_INTERRUPT_PRIORITY, joten sitä
 * kiireellisemmät keskeytykset eivät viivästy koskaan. */
#include "kide_sisainen.h"
#include "mps2.h"

/* Assemblylle sama arvo tekstinä. */
#define MAX_SYSCALL_ASM "0xa0"
_Static_assert(configMAX_SYSCALL_INTERRUPT_PRIORITY == 0xa0u, "BASEPRI");

static volatile uint32_t sisakkaisyys;   /* kriittisten osioiden syvyys */

// @alku kehys
StackType_t *portti_alusta_pino(struct tcb *tcb, StackType_t *huippu) {
    /* AAPCS: pino 8 tavun rajalle. */
    huippu = (StackType_t *)((uintptr_t)huippu & ~(uintptr_t)7u);
    /* Laitteiston tallentama kehys, jonka poikkeuksesta paluu purkaa. */
    *--huippu = 0x01000000u;                       /* xPSR: Thumb */
    *--huippu = (uint32_t)(uintptr_t)tcb->funktio & ~1u;     /* PC */
    *--huippu = (uint32_t)(uintptr_t)kide_tehtava_palasi;   /* LR */
    *--huippu = 0x12121212u;                       /* r12 */
    *--huippu = 0x03030303u;                       /* r3 */
    *--huippu = 0x02020202u;                       /* r2 */
    *--huippu = 0x01010101u;                       /* r1 */
    *--huippu = (uint32_t)(uintptr_t)tcb->parametri;         /* r0 */
    /* Ohjelman (PendSV:n) tallentamat r11..r4. */
    for (uint32_t r = 11; r >= 4; r--) {
        *--huippu = r * 0x01010101u;
    }
    return huippu;
}
// @loppu kehys

// @alku pendsv
__attribute__((naked)) void PendSV_Handler(void) {
    __asm__ volatile(
        "mrs   r0, psp            \n" /* keskeytetyn tehtävän pino      */
        "isb                      \n"
        "ldr   r3, =kide_nykyinen \n"
        "ldr   r2, [r3]           \n"
        "stmdb r0!, {r4-r11}      \n" /* loput rekisterit sen pinoon    */
        "str   r0, [r2]           \n" /* tcb->pino_osoitin = r0         */
        "stmdb sp!, {r3, lr}      \n"
        "mov   r0, #" MAX_SYSCALL_ASM "\n"
        "msr   basepri, r0        \n" /* ytimen tietorakenteet lukkoon  */
        "dsb                      \n"
        "isb                      \n"
        "bl    kide_valitse_seuraava\n"
        "mov   r0, #0             \n"
        "msr   basepri, r0        \n"
        "ldmia sp!, {r3, lr}      \n"
        "ldr   r1, [r3]           \n" /* uusi kide_nykyinen             */
        "ldr   r0, [r1]           \n" /* ja sen pino-osoitin            */
        "ldmia r0!, {r4-r11}      \n"
        "msr   psp, r0            \n"
        "isb                      \n"
        "bx    lr                 \n" /* laitteisto purkaa loput        */
        ".ltorg                   \n");
}
// @loppu pendsv

// @alku svc
/* Ensimmäinen tehtävä käynnistetään SVC-poikkeuksesta palaamalla. */
__attribute__((naked)) void SVC_Handler(void) {
    __asm__ volatile(
        "ldr   r3, =kide_nykyinen \n"
        "ldr   r1, [r3]           \n"
        "ldr   r0, [r1]           \n"
        "ldmia r0!, {r4-r11}      \n"
        "msr   psp, r0            \n"
        "isb                      \n"
        "mov   r0, #0             \n"
        "msr   basepri, r0        \n"
        "orr   lr, lr, #0xd       \n" /* EXC_RETURN: Thread-tila, PSP   */
        "bx    lr                 \n"
        ".ltorg                   \n");
}
// @loppu svc

// @alku kaynnistys
_Noreturn void portti_kaynnista(void) {
    /* PendSV ja SysTick heikoimmalle prioriteetille: tehtävää vaihdetaan
     * vasta, kun kaikki muut keskeytykset ovat valmiita. */
    SCB->SHPR[14 - 4] = configKERNEL_INTERRUPT_PRIORITY;   /* PendSV */
    SCB->SHPR[15 - 4] = configKERNEL_INTERRUPT_PRIORITY;   /* SysTick */
    SYSTICK->LOAD = KELLO_HZ / configTICK_RATE_HZ - 1u;
    SYSTICK->VAL = 0;
    SYSTICK->CTRL = SYSTICK_CTRL_CLKSOURCE | SYSTICK_CTRL_TICKINT |
                    SYSTICK_CTRL_ENABLE;
    sisakkaisyys = 0;
    __asm__ volatile("cpsie i \n svc 0" ::: "memory");
    for (;;) {
    }
}
// @loppu kaynnistys

// @alku systick
void SysTick_Handler(void) {
    uint32_t vanha = portti_peita_isr();
    if (kide_tikki()) {
        portti_vaihda();   /* PendSV ajetaan, kun tämä käsittelijä päättyy */
    }
    portti_palauta_isr(vanha);
}
// @loppu systick

// @alku kriittinen
static inline void aseta_basepri(uint32_t arvo) {
    __asm__ volatile("msr basepri, %0 \n dsb \n isb" ::"r"(arvo) : "memory");
}

void portti_vaihda(void) {
    SCB->ICSR = SCB_ICSR_PENDSVSET;
    muistiaita();
}

void portti_kriittinen_alku(void) {
    aseta_basepri(configMAX_SYSCALL_INTERRUPT_PRIORITY);
    sisakkaisyys++;
}

void portti_kriittinen_loppu(void) {
    if (--sisakkaisyys == 0) {
        aseta_basepri(0);   /* odottava PendSV pääsee nyt ajoon */
    }
}

uint32_t portti_peita_isr(void) {
    uint32_t vanha;
    __asm__ volatile("mrs %0, basepri" : "=r"(vanha));
    aseta_basepri(configMAX_SYSCALL_INTERRUPT_PRIORITY);
    return vanha;
}

void portti_palauta_isr(uint32_t vanha) {
    aseta_basepri(vanha);
}
// @loppu kriittinen

// @alku tarkistus
void portti_tarkista_isr(void) {
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr" : "=r"(ipsr));
    if (ipsr >= 16) {   /* ulkoinen keskeytys: tarkista prioriteetti */
        uint8_t prio = NVIC->IPR[ipsr - 16];
        configASSERT(prio >= configMAX_SYSCALL_INTERRUPT_PRIORITY);
    }
}
// @loppu tarkistus

// @alku kuormita
void portti_kuormita(uint32_t tikit) {
    TaskHandle_t t = kide_nykyinen;
    uint32_t alku = t->ajoaika;
    while (t->ajoaika - alku < tikit) {
        /* laskentaa; tikkikeskeytys kirjaa ajoajan */
    }
}
// @loppu kuormita

void portti_odota(void) {
    odota_keskeytysta();
}
