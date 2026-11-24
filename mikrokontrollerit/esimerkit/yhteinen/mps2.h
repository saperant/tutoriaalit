/* Cortex-M3:n ja QEMU:n mps2-an385-kortin rekisterit.
 *
 * Oikeassa projektissa nämä tulevat valmistajan CMSIS-otsakkeista
 * (core_cm3.h ja laitekohtainen otsake). Tässä ne on kirjoitettu itse,
 * jotta jokainen osoite ja bitti on näkyvissä. */
#ifndef MPS2_H
#define MPS2_H

#include <stddef.h>
#include <stdint.h>

/* Kellotaajuus: mps2-an385:n prosessori ja oheislaitteet, 25 MHz. */
#define KELLO_HZ 25000000u

// @alku uart
/* CMSDK APB UART (ARM DDI 0479). */
typedef struct {
    volatile uint32_t DATA;      /* 0x00 lähetettävä / vastaanotettu */
    volatile uint32_t STATE;     /* 0x04 puskurien tila */
    volatile uint32_t CTRL;      /* 0x08 käyttöönotto, keskeytykset */
    volatile uint32_t INTSTATUS; /* 0x0C luku: tila, kirjoitus: kuittaus */
    volatile uint32_t BAUDDIV;   /* 0x10 kellon jakaja */
} uart_t;

_Static_assert(offsetof(uart_t, BAUDDIV) == 0x10, "UART-kartta");

#define UART0 ((uart_t *)0x40004000u)

#define UART_STATE_TXFULL (1u << 0)
#define UART_STATE_RXFULL (1u << 1)
#define UART_CTRL_TXEN    (1u << 0)
#define UART_CTRL_RXEN    (1u << 1)
#define UART_CTRL_RXINTEN (1u << 3)
#define UART_INT_RX       (1u << 1)
// @loppu uart

// @alku fpgaio
/* FPGA:n I/O-lohko: käyttäjän LEDit ja painikkeet. */
typedef struct {
    volatile uint32_t LED;          /* 0x00 bitit 1..0: LED1, LED0 */
    uint32_t varattu0;              /* 0x04 */
    volatile const uint32_t BUTTON; /* 0x08 vain luku */
} fpgaio_t;

#define FPGAIO ((fpgaio_t *)0x40028000u)
#define LED0   (1u << 0)
#define LED1   (1u << 1)
// @loppu fpgaio

// @alku ajastin
/* CMSDK APB -ajastin (kaksi kappaletta). */
typedef struct {
    volatile uint32_t CTRL;      /* 0x00 bitti 0 päälle, bitti 3 IRQ */
    volatile uint32_t VALUE;     /* 0x04 laskee alaspäin */
    volatile uint32_t RELOAD;    /* 0x08 uusi arvo nollan jälkeen */
    volatile uint32_t INTSTATUS; /* 0x0C luku: tila, kirjoitus: kuittaus */
} ajastin_t;

#define AJASTIN0 ((ajastin_t *)0x40000000u)
#define AJASTIN1 ((ajastin_t *)0x40001000u)
#define AJASTIN_CTRL_EN    (1u << 0)
#define AJASTIN_CTRL_IRQEN (1u << 3)
// @loppu ajastin

/* Keskeytyslinjat (mps2-an385). */
enum {
    UART0RX_IRQn = 0,
    UART0TX_IRQn = 1,
    TIMER0_IRQn = 8,
    TIMER1_IRQn = 9,
    /* Linjat 13..15 (Ethernet, I2S, kosketusnäyttö) ovat QEMU:ssa
     * vapaita; esimerkit laukaisevat niitä ohjelmallisesti. */
    VAPAA0_IRQn = 13,
    VAPAA1_IRQn = 14,
    VAPAA2_IRQn = 15,
};

// @alku systick
/* Ytimen oheislaitteet: System Control Space alkaen 0xE000E000. */
typedef struct {
    volatile uint32_t CTRL;  /* 0xE000E010 */
    volatile uint32_t LOAD;  /* 0xE000E014 24-bittinen alkuarvo */
    volatile uint32_t VAL;   /* 0xE000E018 nykyinen arvo */
    volatile const uint32_t CALIB;
} systick_t;

#define SYSTICK ((systick_t *)0xE000E010u)
#define SYSTICK_CTRL_ENABLE    (1u << 0)
#define SYSTICK_CTRL_TICKINT   (1u << 1)
#define SYSTICK_CTRL_CLKSOURCE (1u << 2) /* 1 = prosessorin kello */
#define SYSTICK_CTRL_COUNTFLAG (1u << 16)
// @loppu systick

// @alku nvic
typedef struct {
    volatile uint32_t ISER[8];  /* 0xE000E100 salli (kirjoita 1) */
    uint32_t varattu0[24];
    volatile uint32_t ICER[8];  /* 0xE000E180 kiellä (kirjoita 1) */
    uint32_t varattu1[24];
    volatile uint32_t ISPR[8];  /* 0xE000E200 aseta odottamaan */
    uint32_t varattu2[24];
    volatile uint32_t ICPR[8];  /* 0xE000E280 poista odotus */
    uint32_t varattu3[24];
    volatile uint32_t IABR[8];  /* 0xE000E300 aktiiviset */
    uint32_t varattu4[56];
    volatile uint8_t IPR[240];  /* 0xE000E400 prioriteetit */
} nvic_t;

_Static_assert(offsetof(nvic_t, IPR) == 0x300, "NVIC-kartta");

#define NVIC ((nvic_t *)0xE000E100u)
// @loppu nvic

// @alku scb
typedef struct {
    volatile const uint32_t CPUID; /* 0xE000ED00 */
    volatile uint32_t ICSR;   /* 0x04 odottavat poikkeukset, PendSV */
    volatile uint32_t VTOR;   /* 0x08 vektoritaulun osoite */
    volatile uint32_t AIRCR;  /* 0x0C prioriteettiryhmät, reset */
    volatile uint32_t SCR;    /* 0x10 lepotilat */
    volatile uint32_t CCR;    /* 0x14 ansat: jako nollalla ym. */
    volatile uint8_t SHPR[12]; /* 0x18 järjestelmäpoikkeusten prio */
    volatile uint32_t SHCSR;  /* 0x24 vikakäsittelijöiden käyttöönotto */
    volatile uint32_t CFSR;   /* 0x28 MemManage-, BusFault-, UsageFault */
    volatile uint32_t HFSR;   /* 0x2C HardFaultin syy */
    volatile uint32_t DFSR;   /* 0x30 */
    volatile uint32_t MMFAR;  /* 0x34 MemManage-osoite */
    volatile uint32_t BFAR;   /* 0x38 BusFault-osoite */
} scb_t;

_Static_assert(offsetof(scb_t, BFAR) == 0x38, "SCB-kartta");

#define SCB ((scb_t *)0xE000ED00u)
// @loppu scb

#define SCB_ICSR_PENDSVSET   (1u << 28)
#define SCB_AIRCR_AVAIMET    (0x05FAu << 16)
#define SCB_AIRCR_SYSRESETREQ (1u << 2)
#define SCB_SCR_SLEEPONEXIT  (1u << 1)
#define SCB_SCR_SLEEPDEEP    (1u << 2)
#define SCB_SCR_SEVONPEND    (1u << 4)
#define SCB_CCR_DIV_0_TRP    (1u << 4)
#define SCB_SHCSR_MEMFAULTENA (1u << 16)
#define SCB_SHCSR_BUSFAULTENA (1u << 17)
#define SCB_SHCSR_USGFAULTENA (1u << 18)

// @alku nvic-apu
/* CMSIS:n NVIC_EnableIRQ, NVIC_DisableIRQ, NVIC_SetPendingIRQ ja
 * NVIC_SetPriority vastaavat näitä. */
static inline void nvic_salli(unsigned irq) {
    NVIC->ISER[irq / 32] = 1u << (irq % 32);
}
static inline void nvic_kiella(unsigned irq) {
    NVIC->ICER[irq / 32] = 1u << (irq % 32);
}
static inline void nvic_laukaise(unsigned irq) {
    NVIC->ISPR[irq / 32] = 1u << (irq % 32);
}
/* Prioriteetti 0..7: Cortex-M3-piirissä toteutettu kolme ylintä
 * bittiä; pienempi luku on kiireellisempi. */
static inline void nvic_prioriteetti(unsigned irq, unsigned prio) {
    NVIC->IPR[irq] = (uint8_t)(prio << 5);
}
// @loppu nvic-apu

// @alku sisaiset
/* Käskyt, joille C:ssä ei ole vastinetta (CMSIS: __disable_irq ym.). */
static inline void keskeytykset_pois(void) {
    __asm__ volatile("cpsid i" ::: "memory");
}
static inline void keskeytykset_paalle(void) {
    __asm__ volatile("cpsie i" ::: "memory");
}
static inline uint32_t lue_primask(void) {
    uint32_t arvo;
    __asm__ volatile("mrs %0, primask" : "=r"(arvo));
    return arvo;
}
static inline void aseta_primask(uint32_t arvo) {
    __asm__ volatile("msr primask, %0" ::"r"(arvo) : "memory");
}
static inline void odota_keskeytysta(void) {
    __asm__ volatile("wfi" ::: "memory");
}
static inline void odota_tapahtumaa(void) {
    __asm__ volatile("wfe" ::: "memory");
}
static inline void laheta_tapahtuma(void) {
    __asm__ volatile("sev" ::: "memory");
}
static inline void muistiaita(void) {
    __asm__ volatile("dsb\n\tisb" ::: "memory");
}
// @loppu sisaiset

#endif
