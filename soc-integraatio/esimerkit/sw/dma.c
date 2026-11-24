/* DMA: kopiointi suorittimella ja DMA-ohjaimella, keskeytys ja virhe. */
#include <stdint.h>

#include "soc.h"
#include "tuki.h"

#define SANAT 64u

static uint32_t lahde[SANAT], kohde_cpu[SANAT], kohde_dma[SANAT];
static volatile uint32_t dma_tila;

void ulkoinen_keskeytys(void)
{
    uint32_t id = PLIC->LUNASTA;
    if (id == PLIC_DMA) {
        dma_tila = DMA->TILA;
        DMA->TILA = DMA_VALMIS | DMA_VIRHE;  /* W1C: keskeytys pois */
    }
    PLIC->LUNASTA = id;
}

/* @alku kaynnista */
static uint32_t dma_kopioi(const void *mista, void *minne, uint32_t sanat)
{
    dma_tila = 0;
    DMA->LAHDE = (uint32_t)(uintptr_t)mista;
    DMA->KOHDE = (uint32_t)(uintptr_t)minne;
    DMA->MAARA = sanat;
    DMA->OHJAUS = DMA_KAYNNISTA | DMA_SALLI_KESK;
    while (dma_tila == 0) {
        /* suoritin voisi tehdä muuta; tässä se odottaa keskeytystä */
    }
    return dma_tila;
}
/* @loppu kaynnista */

static int vertaa(const uint32_t *a, const uint32_t *b)
{
    for (uint32_t i = 0; i < SANAT; i++)
        if (a[i] != b[i]) return 0;
    return 1;
}

int main(void)
{
    for (uint32_t i = 0; i < SANAT; i++)
        lahde[i] = (i * 0x01010101u) ^ 0xA5A5A5A5u;

    PLIC->SALLI = 1u << PLIC_DMA;
    csr_aseta(mie, MIE_MEIE);
    csr_aseta(mstatus, MSTATUS_MIE);

    /* @alku vertailu */
    uint32_t t0 = csr_lue(mcycle);
    for (uint32_t i = 0; i < SANAT; i++) kohde_cpu[i] = lahde[i];
    uint32_t t1 = csr_lue(mcycle);
    uint32_t tila = dma_kopioi(lahde, kohde_dma, SANAT);
    uint32_t t2 = csr_lue(mcycle);
    /* @loppu vertailu */

    tulosta("suoritin: ");
    tulosta_luku(t1 - t0);
    tulosta(" jaksoa, ");
    tulosta(vertaa(lahde, kohde_cpu) ? "oikein\n" : "VÄÄRIN\n");
    tulosta("DMA:      ");
    tulosta_luku(t2 - t1);
    tulosta(" jaksoa, ");
    tulosta(vertaa(lahde, kohde_dma) ? "oikein" : "VÄÄRIN");
    tulosta(", TILA ");
    tulosta_hex(tila);
    tulosta("\n");

    /* @alku virhe */
    tila = dma_kopioi(lahde, (void *)0x20000000u, 4);  /* ei muistia */
    tulosta("DMA kartoittamattomaan osoitteeseen: TILA ");
    tulosta_hex(tila);
    tulosta((tila & DMA_VIRHE) ? " (väylävirhe)\n" : "\n");
    /* @loppu virhe */
    return 0;
}
