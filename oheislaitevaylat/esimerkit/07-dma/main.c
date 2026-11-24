/* DMA muistista muistiin: kopio, kuvaajaketju (scatter-gather) ja
 * yleinen virhe. Ajetaan mps2-an505-kortilla, jonka PL081 on QEMU:n
 * mallissa käytettävissä. */
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "konsoli.h"
#include "mps2.h"
#include "pl081.h"

// @alku kaynnista
/* Käynnistää kanavan 0. Ennen käynnistystä DSB varmistaa, että
 * suorittimen kirjoitukset lähdepuskuriin ja kuvaajiin ovat
 * muistissa: DMA lukee muistia suoraan, ei suorittimen
 * kirjoituspuskurista. */
static void kaynnista(const pl081_kuvaaja_t *eka, uint32_t asetus) {
    pl081_kanava_t *k = &DMA0->KANAVA[0];
    DMA0->INTTCCLEAR = 1u;
    DMA0->INTERRCLR = 1u;
    k->LAHDE = eka->lahde;
    k->KOHDE = eka->kohde;
    k->LLI = eka->seuraava;
    k->OHJAUS = eka->ohjaus;
    dsb();
    k->ASETUS = asetus | ASETUS_KAYTOSSA;
}

static int kaynnissa(void) {
    return (DMA0->ENBLDCHNS & 1u) != 0;
}
// @loppu kaynnista

// @alku kopio
static uint32_t lahde[64];
static uint32_t kohde[64];

static void kopio(void) {
    for (uint32_t i = 0; i < 64; i++) {
        lahde[i] = i * 0x01010101u;
    }
    const pl081_kuvaaja_t k = {
        (uint32_t)lahde, (uint32_t)kohde, 0,
        OHJAUS_KOKO(64) | OHJAUS_LEVEYS_32 | OHJAUS_LAHDE_KASVA |
            OHJAUS_KOHDE_KASVA};
    kaynnista(&k, 0);
    while (kaynnissa()) {
        /* Kanava poistuu käytöstä, kun koko siirto on tehty. */
    }
    dsb();
    tulosta("kopio: %s, kohde[63] = %08x\n",
            memcmp(lahde, kohde, sizeof lahde) == 0 ? "ok" : "VIRHE",
            (unsigned)kohde[63]);
}
// @loppu kopio

// @alku ketju
static volatile int ketju_valmis;

/* Valmistuneiden siirtojen käsittely. Oikeassa ohjelmassa tätä
 * kutsuisi DMA-ohjaimen keskeytyskäsittelijä; QEMU:n mps2-an505-
 * mallissa DMA:n keskeytys ei kuitenkaan päädy NVIC:iin, joten
 * esimerkki kutsuu sitä odotussilmukasta. */
static void dma_valmistuneet(void) {
    if (DMA0->INTTCSTATUS & 1u) {
        DMA0->INTTCCLEAR = 1u; /* kuittaus, kuten keskeytyksessä */
        ketju_valmis = 1;
    }
}

/* Kootaan viesti kolmesta erillisestä palasta yhteen puskuriin.
 * Kanava lataa seuraavan kuvaajan itse; keskeytys tulee vasta
 * viimeisen palan jälkeen. */
static void ketju(void) {
    static const char otsake[] = "MITTAUS ";
    static const char arvo[] = "1600 mV";
    static const char loppu[] = "\r\n";
    static char viesti[32];
    static pl081_kuvaaja_t kuvaajat[3];
    const uint32_t tavut = OHJAUS_LEVEYS_8 | OHJAUS_LAHDE_KASVA |
                           OHJAUS_KOHDE_KASVA;
    char *paikka = viesti;
    kuvaajat[0] = (pl081_kuvaaja_t){(uint32_t)otsake, (uint32_t)paikka,
                                    (uint32_t)&kuvaajat[1],
                                    tavut | OHJAUS_KOKO(8)};
    paikka += 8;
    kuvaajat[1] = (pl081_kuvaaja_t){(uint32_t)arvo, (uint32_t)paikka,
                                    (uint32_t)&kuvaajat[2],
                                    tavut | OHJAUS_KOKO(7)};
    paikka += 7;
    kuvaajat[2] = (pl081_kuvaaja_t){(uint32_t)loppu, (uint32_t)paikka, 0,
                                    tavut | OHJAUS_KOKO(2) |
                                        OHJAUS_KESKEYTA};
    ketju_valmis = 0;
    kaynnista(&kuvaajat[0], ASETUS_ITC | ASETUS_IE);
    while (!ketju_valmis) {
        dma_valmistuneet();
    }
    dsb();
    int ok = memcmp(viesti, "MITTAUS 1600 mV\r\n", 17) == 0;
    viesti[15] = '\0'; /* tulostetaan ilman rivinvaihtoa */
    tulosta("ketju: \"%s\" + CRLF, %s\n", viesti, ok ? "ok" : "VIRHE");
}
// @loppu ketju

// @alku koko
/* Yleinen virhe: siirron koko annetaan tavuina, vaikka se lasketaan
 * lähteen leveyden yksiköissä. 8 sanan kopiosta tulee 32 sanan
 * kopio, joka kirjoittaa puskurin ohi. */
static void vaara_koko(void) {
    static uint32_t pieni_lahde[32];
    static struct {
        uint32_t data[8];
        uint32_t vartija[24];
    } pieni;
    for (unsigned i = 0; i < 24; i++) {
        pieni.vartija[i] = 0xDEADBEEFu;
    }
    const pl081_kuvaaja_t k = {
        (uint32_t)pieni_lahde, (uint32_t)pieni.data, 0,
        OHJAUS_KOKO(sizeof pieni.data) | OHJAUS_LEVEYS_32 |
            OHJAUS_LAHDE_KASVA | OHJAUS_KOHDE_KASVA};
    kaynnista(&k, 0);
    while (kaynnissa()) {
    }
    dsb();
    unsigned rikki = 0;
    for (unsigned i = 0; i < 24; i++) {
        rikki += pieni.vartija[i] != 0xDEADBEEFu;
    }
    tulosta("vaara koko: %u/24 vartijasanaa ylikirjoitettu\n", rikki);
}
// @loppu koko

int main(void) {
    konsoli_alusta();
    DMA0->CONFIG = 1u; /* ohjain käyttöön */
    kopio();
    ketju();
    vaara_koko();
    return 0;
}
