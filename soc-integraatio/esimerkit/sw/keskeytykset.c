/* Keskeytykset: CLINTin ajastin ja GPIO PLICin kautta. */
#include <stdint.h>

#include "soc.h"
#include "tuki.h"

#define VALI 400u                       /* ajastimen väli jaksoina */

static volatile uint32_t tikit;
static volatile uint32_t reunoja;

/* @alku ajastin */
static void aseta_vertailu(uint64_t arvo)
{
    /* Kolmen kirjoituksen järjestys estää väliaikaisen, liian pienen
     * vertailuarvon ja siten aiheettoman keskeytyksen. */
    CLINT->MTIMECMP_L = 0xFFFFFFFFu;
    CLINT->MTIMECMP_H = (uint32_t)(arvo >> 32);
    CLINT->MTIMECMP_L = (uint32_t)arvo;
}

static uint64_t mtime(void)
{
    uint32_t yla, ala;
    do {                                /* ylempi puolisko ei saa vaihtua */
        yla = CLINT->MTIME_H;
        ala = CLINT->MTIME_L;
    } while (yla != CLINT->MTIME_H);
    return ((uint64_t)yla << 32) | ala;
}

void ajastin_keskeytys(void)
{
    tikit++;
    tulosta("ajastin: tikki ");
    tulosta_luku(tikit);
    tulosta("\n");
    if (tikit < 3) aseta_vertailu(mtime() + VALI);
    else aseta_vertailu(UINT64_MAX);    /* kuittaa ja pysäytä */
}
/* @loppu ajastin */

/* @alku ulkoinen */
void ulkoinen_keskeytys(void)
{
    uint32_t lahde = PLIC->LUNASTA;     /* lunastus (claim) */
    if (lahde == PLIC_GPIO) {
        uint32_t reunat = GPIO->REUNAT;
        GPIO->REUNAT = reunat;          /* W1C: kuittaa havaitut reunat */
        reunoja++;
        tulosta("GPIO: reunat ");
        tulosta_hex(reunat);
        tulosta("\n");
    }
    PLIC->LUNASTA = lahde;              /* valmis (complete) */
}
/* @loppu ulkoinen */

int main(void)
{
    /* @alku salli */
    aseta_vertailu(mtime() + VALI);
    csr_aseta(mie, MIE_MTIE | MIE_MEIE);
    csr_aseta(mstatus, MSTATUS_MIE);
    /* @loppu salli */
    while (tikit < 3) {
        /* pääohjelma voisi tehdä muuta työtä */
    }

    /* @alku gpio */
    GPIO->SALLI = 0x01u;                /* keskeytys tulon 0 reunasta */
    PLIC->SALLI = 1u << PLIC_GPIO;
    GPIO->ULOS = 0x01u;                 /* silmukka: lähtö 0 → tulo 0 */
    while (reunoja < 1) {
    }
    GPIO->ULOS = 0x00u;                 /* laskeva reuna: ei keskeytystä */
    GPIO->ULOS = 0x03u;                 /* kaksi nousevaa reunaa */
    while (reunoja < 2) {
    }
    /* @loppu gpio */
    tulosta("keskeytyksiä: ajastin 3, GPIO ");
    tulosta_luku(reunoja);
    tulosta("\n");
    return 0;
}
