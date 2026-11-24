/* Pikku-SoC:n muistikartta ja oheislaitteiden rekisterit.
 *
 * Rekisterit kuvataan rakenteina, joiden kentät ovat volatile: kääntäjä
 * ei saa poistaa, yhdistää eikä järjestää MMIO-luku- ja -kirjoituksia
 * uudelleen. SYSCONin ja GPIO:n rakenteet on generoitu kuvauksista. */
#ifndef SOC_H
#define SOC_H

#include <stdint.h>

#include "gpio_regs.h"
#include "syscon_regs.h"

/* @alku kartta */
#define RAM_KANTA     0x00000000u
#define UART_KANTA    0x10000000u
#define SYSCON_KANTA  0x10001000u
#define GPIO_KANTA    0x10002000u
#define DMA_KANTA     0x10003000u
#define CLINT_KANTA   0x10004000u
#define PLIC_KANTA    0x10005000u
/* @loppu kartta */

typedef struct {
    volatile uint32_t DATA;
    volatile const uint32_t TILA;       /* bitti 0: lähetys käynnissä */
    volatile uint32_t JAKAJA;
} uart_regs_t;

typedef struct {
    volatile uint32_t MTIME_L, MTIME_H;
    volatile uint32_t MTIMECMP_L, MTIMECMP_H;
} clint_regs_t;

typedef struct {
    volatile const uint32_t ODOTTAA;
    volatile uint32_t SALLI;
    volatile uint32_t LUNASTA;          /* luku: lunasta, kirjoitus: valmis */
} plic_regs_t;

typedef struct {
    volatile uint32_t LAHDE, KOHDE, MAARA, OHJAUS, TILA;
} dma_regs_t;

#define UART   ((uart_regs_t *)UART_KANTA)
#define SYSCON ((syscon_regs_t *)SYSCON_KANTA)
#define GPIO   ((gpio_regs_t *)GPIO_KANTA)
#define DMA    ((dma_regs_t *)DMA_KANTA)
#define CLINT  ((clint_regs_t *)CLINT_KANTA)
#define PLIC   ((plic_regs_t *)PLIC_KANTA)

#define PLIC_GPIO 1u
#define PLIC_DMA  2u

#define DMA_KAYNNISTA  (1u << 0)
#define DMA_SALLI_KESK (1u << 1)
#define DMA_KAYNNISSA  (1u << 0)
#define DMA_VALMIS     (1u << 1)
#define DMA_VIRHE      (1u << 2)

/* CSR-käskyt. */
#define csr_lue(csr) ({ uint32_t _v; \
    __asm__ volatile("csrr %0, " #csr : "=r"(_v)); _v; })
#define csr_kirjoita(csr, v) \
    __asm__ volatile("csrw " #csr ", %0" : : "r"(v))
#define csr_aseta(csr, v) \
    __asm__ volatile("csrs " #csr ", %0" : : "r"(v))
#define csr_nollaa(csr, v) \
    __asm__ volatile("csrc " #csr ", %0" : : "r"(v))

#define MSTATUS_MIE (1u << 3)
#define MIE_MTIE    (1u << 7)
#define MIE_MEIE    (1u << 11)

#endif
