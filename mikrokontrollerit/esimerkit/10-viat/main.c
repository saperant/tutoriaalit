/* Vikapoikkeukset: HardFault, BusFault, UsageFault ja MemManage.
 * Käsittelijä tulostaa syyn ja jatkaa vian aiheuttaneen käskyn ohi,
 * jotta kaikki tapaukset nähdään yhdellä ajolla. */
#include <stdint.h>

#include "konsoli.h"
#include "mps2.h"

// @alku kehys
/* Poikkeuksen alussa prosessori tallentaa nämä pinoon. */
typedef struct {
    uint32_t r0, r1, r2, r3, r12, lr, pc, xpsr;
} kehys_t;
// @loppu kehys

/* Vikakohtien osoitteet: assembly-nimiöt alla olevissa funktioissa. */
extern const char vika_luku[], vika_jako[], vika_kasky[], vika_kirjoitus[];
static void parillinen_kohde(void);

static const char *kohta(uint32_t pc) {
    if (pc == (uint32_t)vika_luku) {
        return "vika_luku";
    }
    if (pc == (uint32_t)vika_jako) {
        return "vika_jako";
    }
    if (pc == (uint32_t)vika_kasky) {
        return "vika_kasky";
    }
    if (pc == (uint32_t)vika_kirjoitus) {
        return "vika_kirjoitus";
    }
    if (pc == ((uint32_t)parillinen_kohde & ~1u)) {
        return "parillinen_kohde";
    }
    return "tuntematon";
}

// @alku bitit
static const struct {
    uint32_t maski;
    const char *nimi;
} cfsr_bitit[] = {
    {1u << 1, "DACCVIOL: muistisuojaus esti datan käsittelyn"},
    {1u << 7, "MMARVALID: MMFAR sisältää osoitteen"},
    {1u << 9, "PRECISERR: väylävirhe, tarkka osoite"},
    {1u << 10, "IMPRECISERR: väylävirhe, epätarkka"},
    {1u << 12, "STKERR: pinoon tallennus epäonnistui"},
    {1u << 15, "BFARVALID: BFAR sisältää osoitteen"},
    {1u << 16, "UNDEFINSTR: tuntematon käsky"},
    {1u << 17, "INVSTATE: Thumb-bitti nolla"},
    {1u << 24, "UNALIGNED: tasaamaton osoite"},
    {1u << 25, "DIVBYZERO: jako nollalla"},
};
// @loppu bitit

// @alku kasittely
static unsigned kaskyn_pituus(uint32_t pc) {
    uint16_t puolisana = *(const uint16_t *)pc;
    /* Thumb-2: 32-bittisen käskyn ylin viisi bittiä 11101..11111. */
    return (puolisana >> 11) >= 0x1Du ? 4u : 2u;
}

void vian_kasittely(kehys_t *kehys) {
    static const char *const nimet[] = {
        [3] = "HardFault", [4] = "MemManage", [5] = "BusFault",
        [6] = "UsageFault"};
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr" : "=r"(ipsr));
    uint32_t cfsr = SCB->CFSR, hfsr = SCB->HFSR;

    tulosta("  %s, PC = %s\n", nimet[ipsr], kohta(kehys->pc));
    if (hfsr & (1u << 30)) {
        tulosta("    HFSR.FORCED: eskaloitunut, vikakäsittelijä pois\n");
    }
    for (unsigned i = 0; i < sizeof cfsr_bitit / sizeof cfsr_bitit[0];
         i++) {
        if (cfsr & cfsr_bitit[i].maski) {
            tulosta("    %s\n", cfsr_bitit[i].nimi);
        }
    }
    if (cfsr & (1u << 15)) {
        tulosta("    BFAR = 0x%08x\n", (unsigned)SCB->BFAR);
    }
    if (cfsr & (1u << 7)) {
        tulosta("    MMFAR = 0x%08x\n", (unsigned)SCB->MMFAR);
    }

    SCB->CFSR = cfsr;                  /* kuittaus: kirjoita 1 */
    SCB->HFSR = hfsr;
    if (cfsr & (1u << 17)) {
        kehys->pc = kehys->lr & ~1u;   /* palataan kutsujaan */
        kehys->xpsr |= 1u << 24;       /* T-bitti takaisin */
    } else {
        kehys->pc += kaskyn_pituus(kehys->pc);
    }
}
// @loppu kasittely

// @alku stub
__attribute__((naked)) void HardFault_Handler(void) {
    __asm__ volatile(
        "tst   lr, #4\n\t"
        "ite   eq\n\t"
        "mrseq r0, msp\n\t"
        "mrsne r0, psp\n\t"
        "b     vian_kasittely\n\t");
}
void MemManage_Handler(void) __attribute__((alias("HardFault_Handler")));
void BusFault_Handler(void) __attribute__((alias("HardFault_Handler")));
void UsageFault_Handler(void) __attribute__((alias("HardFault_Handler")));
// @loppu stub

// @alku viat
/* noinline: nimiö saa esiintyä ohjelmassa vain kerran. */
#define KERRAN __attribute__((noinline, noclone))

KERRAN static uint32_t lue(uint32_t osoite) {
    uint32_t arvo = 0xDEADu;
    __asm__ volatile(".global vika_luku\nvika_luku:\n\t"
                     "ldr %0, [%1]"
                     : "+r"(arvo) : "r"(osoite) : "memory");
    return arvo;
}

KERRAN static uint32_t jaa(uint32_t a, uint32_t b) {
    uint32_t tulos;
    __asm__ volatile(".global vika_jako\nvika_jako:\n\t"
                     "udiv %0, %1, %2"
                     : "=r"(tulos) : "r"(a), "r"(b));
    return tulos;
}

KERRAN static void tuntematon_kasky(void) {
    __asm__ volatile(".global vika_kasky\nvika_kasky:\n\t"
                     "udf #0");
}

KERRAN static void kirjoita(volatile uint32_t *osoite, uint32_t arvo) {
    __asm__ volatile(".global vika_kirjoitus\nvika_kirjoitus:\n\t"
                     "str %1, [%0]"
                     ::"r"(osoite), "r"(arvo) : "memory");
}

KERRAN static void parillinen_kohde(void) {
    tulosta("ei pitäisi tulostua\n");
}
// @loppu viat

// @alku mpu
#define MPU_CTRL (*(volatile uint32_t *)0xE000ED94u)
#define MPU_RNR  (*(volatile uint32_t *)0xE000ED98u)
#define MPU_RBAR (*(volatile uint32_t *)0xE000ED9Cu)
#define MPU_RASR (*(volatile uint32_t *)0xE000EDA0u)

/* Alueen koko on kahden potenssi ja alku tasattu koon mukaan. */
__attribute__((aligned(32))) static volatile uint32_t suojattu[8];

static void mpu_lukitse(void) {
    MPU_RNR = 0;                              /* alue 0 */
    MPU_RBAR = (uint32_t)suojattu;
    MPU_RASR = (1u << 28)                     /* XN: ei suoritusta */
             | (6u << 24)                     /* AP: vain luku */
             | (4u << 1)                      /* SIZE: 2^(4+1) = 32 */
             | 1u;                            /* ENABLE */
    MPU_CTRL = (1u << 2) | 1u;   /* PRIVDEFENA: muu muisti oletuksin */
    muistiaita();
}
// @loppu mpu

int main(void) {
    konsoli_alusta();
    // @alku main
    tulosta("1) luku kuvaamattomasta osoitteesta\n");
    lue(0x50000000u);

    SCB->SHCSR |= SCB_SHCSR_MEMFAULTENA | SCB_SHCSR_BUSFAULTENA |
                  SCB_SHCSR_USGFAULTENA;
    tulosta("2) sama, vikakäsittelijät sallittu\n");
    lue(0x50000000u);

    tulosta("3) jako nollalla: %u\n", (unsigned)jaa(7, 0));
    SCB->CCR |= SCB_CCR_DIV_0_TRP;
    tulosta("4) jako nollalla, DIV_0_TRP\n");
    jaa(7, 0);

    tulosta("5) tuntematon käsky\n");
    tuntematon_kasky();

    tulosta("6) hyppy parilliseen osoitteeseen\n");
    void (*osoitin)(void) =
        (void (*)(void))((uint32_t)parillinen_kohde & ~1u);
    osoitin();

    mpu_lukitse();
    tulosta("7) kirjoitus MPU:n suojaamaan muistiin (0x%08x)\n",
            (unsigned)suojattu);
    tulosta("   luku onnistuu: %u\n", (unsigned)suojattu[0]);
    kirjoita(&suojattu[1], 1);
    tulosta("kaikki viat käsitelty\n");
    // @loppu main
    return 0;
}
