/* QEMU:n MPS2-korttien rekisterit: mps2-an385 (Cortex-M3) ja
 * mps2-an505 (Cortex-M33, vain DMA-esimerkki, makro AN505).
 *
 * Oikeassa projektissa nämä tulevat valmistajan CMSIS-otsakkeista.
 * Tässä ne on kirjoitettu itse, jotta jokainen osoite ja bitti on
 * näkyvissä. Ytimen rekisterit ja UART on esitelty paketissa
 * Mikrokontrollerit ja bare-metal-ohjelmointi. */
#ifndef MPS2_H
#define MPS2_H

#include <stddef.h>
#include <stdint.h>

/* Kellotaajuus: prosessori ja oheislaitteet, 25 MHz. */
#define KELLO_HZ 25000000u

/* CMSDK APB UART (ARM DDI 0479). */
typedef struct {
    volatile uint32_t DATA;      /* 0x00 lähetettävä / vastaanotettu */
    volatile uint32_t STATE;     /* 0x04 puskurien tila */
    volatile uint32_t CTRL;      /* 0x08 käyttöönotto, keskeytykset */
    volatile uint32_t INTSTATUS; /* 0x0C luku: tila, kirjoitus: kuittaus */
    volatile uint32_t BAUDDIV;   /* 0x10 kellon jakaja */
} uart_t;

_Static_assert(offsetof(uart_t, BAUDDIV) == 0x10, "UART-kartta");

#ifdef AN505
#define UART0 ((uart_t *)0x50200000u) /* turvallisen tilan alias */
#else
#define UART0 ((uart_t *)0x40004000u)
#define UART1 ((uart_t *)0x40005000u)
#endif

#define UART_STATE_TXFULL (1u << 0)
#define UART_STATE_RXFULL (1u << 1)
#define UART_CTRL_TXEN    (1u << 0)
#define UART_CTRL_RXEN    (1u << 1)
#define UART_CTRL_TXINTEN (1u << 2)
#define UART_CTRL_RXINTEN (1u << 3)
#define UART_INT_TX       (1u << 0)
#define UART_INT_RX       (1u << 1)

// @alku pl022
/* PL022 Synchronous Serial Port (ARM DDI 0194). */
typedef struct {
    volatile uint32_t CR0;      /* 0x00 sanan koko, muoto, CPOL, CPHA */
    volatile uint32_t CR1;      /* 0x04 LBM, SSE, MS */
    volatile uint32_t DR;       /* 0x08 FIFO: kirjoitus lähettää */
    volatile const uint32_t SR; /* 0x0C FIFOjen tila */
    volatile uint32_t CPSR;     /* 0x10 esijakaja, parillinen 2..254 */
    volatile uint32_t IMSC;     /* 0x14 keskeytysmaski */
    volatile const uint32_t RIS; /* 0x18 keskeytykset ennen maskia */
    volatile const uint32_t MIS; /* 0x1C keskeytykset maskin jälkeen */
    volatile uint32_t ICR;      /* 0x20 kuittaus */
    volatile uint32_t DMACR;    /* 0x24 DMA-pyynnöt */
} pl022_t;

_Static_assert(offsetof(pl022_t, DMACR) == 0x24, "PL022-kartta");

#define PL022_CR0_DSS(bitit) ((uint32_t)(bitit) - 1u) /* 4..16 */
#define PL022_CR0_SPO      (1u << 6)   /* CPOL */
#define PL022_CR0_SPH      (1u << 7)   /* CPHA */
#define PL022_CR0_SCR(n)   ((uint32_t)(n) << 8)
#define PL022_CR1_LBM      (1u << 0)   /* sisäinen silmukka */
#define PL022_CR1_SSE      (1u << 1)   /* käytössä */
#define PL022_SR_TFE       (1u << 0)   /* lähetys-FIFO tyhjä */
#define PL022_SR_TNF       (1u << 1)   /* lähetys-FIFOssa tilaa */
#define PL022_SR_RNE       (1u << 2)   /* vastaanotto-FIFOssa dataa */
#define PL022_SR_BSY       (1u << 4)   /* siirto käynnissä */
// @loppu pl022

/* QEMU kytkee komentorivillä annetun SPI-laitteen tähän väylään. */
#define SPI_ADC ((pl022_t *)0x40027000u)

// @alku sbcon
/* SBCon: kaksijohtiminen väylä, jonka linjoja ohjelma liikuttaa
 * itse. Bitti 1 vapauttaa linjan (vetovastus nostaa sen), bitti 0
 * vetää sen alas. Luku palauttaa linjojen todellisen tilan. */
typedef struct {
    volatile uint32_t CTRL; /* 0x00 luku: linjat, kirjoitus: vapauta */
    volatile uint32_t CLR;  /* 0x04 kirjoitus: vedä alas */
} sbcon_t;

#define SBCON_SCL (1u << 0)
#define SBCON_SDA (1u << 1)

/* QEMU kytkee komentorivillä annetut I2C-laitteet tähän väylään. */
#define I2C_ANTURIT ((sbcon_t *)0x4002A000u)
// @loppu sbcon

/* Keskeytyslinjat (mps2-an385). */
enum {
    UART0RX_IRQn = 0,
    UART0TX_IRQn = 1,
    UART1RX_IRQn = 2,
    UART1TX_IRQn = 3,
};

typedef struct {
    volatile uint32_t ISER[8];  /* 0xE000E100 salli (kirjoita 1) */
    uint32_t varattu0[24];
    volatile uint32_t ICER[8];  /* 0xE000E180 kiellä (kirjoita 1) */
    uint32_t varattu1[24];
    volatile uint32_t ISPR[8];  /* 0xE000E200 aseta odottamaan */
    uint32_t varattu2[24];
    volatile uint32_t ICPR[8];  /* 0xE000E280 poista odotus */
} nvic_t;

#define NVIC ((nvic_t *)0xE000E100u)

static inline void nvic_salli(unsigned irq) {
    NVIC->ISER[irq / 32] = 1u << (irq % 32);
}
static inline void nvic_laukaise(unsigned irq) {
    NVIC->ISPR[irq / 32] = 1u << (irq % 32);
}

/* Käskyt, joille C:ssä ei ole vastinetta (CMSIS: __disable_irq ym.). */
static inline uint32_t lue_primask(void) {
    uint32_t arvo;
    __asm__ volatile("mrs %0, primask" : "=r"(arvo));
    return arvo;
}
static inline void keskeytykset_pois(void) {
    __asm__ volatile("cpsid i" ::: "memory");
}
static inline void aseta_primask(uint32_t arvo) {
    __asm__ volatile("msr primask, %0" ::"r"(arvo) : "memory");
}
static inline void odota_keskeytysta(void) {
    __asm__ volatile("wfi" ::: "memory");
}
// @alku aidat
/* DMB: muistioperaatiot näkyvät muille väylän isännille tässä
 * järjestyksessä. DSB: lisäksi odotetaan, että ne ovat valmiit. */
static inline void dmb(void) {
    __asm__ volatile("dmb" ::: "memory");
}
static inline void dsb(void) {
    __asm__ volatile("dsb" ::: "memory");
}
// @loppu aidat

#endif
