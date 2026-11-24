/* PL081 DMA Controller (ARM DDI 0218): kaksi kanavaa. mps2-an505:n
 * DMA0 on turvallisen tilan osoitteessa 0x50110000. */
#ifndef PL081_H
#define PL081_H

#include <stddef.h>
#include <stdint.h>

// @alku rekisterit
typedef struct {
    volatile uint32_t LAHDE;   /* 0x00 SrcAddr */
    volatile uint32_t KOHDE;   /* 0x04 DestAddr */
    volatile uint32_t LLI;     /* 0x08 seuraava kuvaaja tai 0 */
    volatile uint32_t OHJAUS;  /* 0x0C Control: koko, leveys, kasvatus */
    volatile uint32_t ASETUS;  /* 0x10 Configuration: käyttöön, vuo */
    uint32_t varattu[3];
} pl081_kanava_t;

typedef struct {
    volatile const uint32_t INTSTATUS;   /* 0x000 */
    volatile const uint32_t INTTCSTATUS; /* 0x004 valmistuneet */
    volatile uint32_t INTTCCLEAR;        /* 0x008 */
    volatile const uint32_t INTERRSTATUS; /* 0x00C virheet */
    volatile uint32_t INTERRCLR;         /* 0x010 */
    uint32_t varattu0[2];
    volatile const uint32_t ENBLDCHNS;   /* 0x01C käynnissä olevat */
    uint32_t varattu1[4];
    volatile uint32_t CONFIG;            /* 0x030 bitti 0: käytössä */
    uint32_t varattu2[51];
    pl081_kanava_t KANAVA[2];            /* 0x100, 0x120 */
} pl081_t;

_Static_assert(offsetof(pl081_t, CONFIG) == 0x030, "PL081-kartta");
_Static_assert(offsetof(pl081_t, KANAVA) == 0x100, "PL081-kartta");

#define DMA0 ((pl081_t *)0x50110000u)

/* OHJAUS: siirron koko lähteen leveyden yksiköissä (12 bittiä). */
#define OHJAUS_KOKO(n)     ((uint32_t)(n) & 0xFFFu)
#define OHJAUS_LEVEYS_8    (0u << 18 | 0u << 21)
#define OHJAUS_LEVEYS_32   (2u << 18 | 2u << 21)
#define OHJAUS_LAHDE_KASVA (1u << 26)
#define OHJAUS_KOHDE_KASVA (1u << 27)
#define OHJAUS_KESKEYTA    (1u << 31) /* TC-keskeytys tämän jälkeen */

/* ASETUS: vuonohjaus 0 = muistista muistiin, DMA-ohjain päättää. */
#define ASETUS_KAYTOSSA (1u << 0)
#define ASETUS_ITC      (1u << 15) /* TC-keskeytys sallittu */
#define ASETUS_IE       (1u << 14) /* virhekeskeytys sallittu */

/* Kuvaaja muistissa: kanava lataa seuraavan itse (scatter-gather). */
typedef struct {
    uint32_t lahde;
    uint32_t kohde;
    uint32_t seuraava; /* seuraavan kuvaajan osoite tai 0 */
    uint32_t ohjaus;
} pl081_kuvaaja_t;
// @loppu rekisterit

#endif
