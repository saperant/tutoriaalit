/* PL022-SPI-isännän ajuri. */
#include "pl022.h"

/* FIFOn syvyys: enintään näin monta kehystä matkalla kerrallaan. */
#define FIFO 8u
/* Montako kertaa tilarekisteriä luetaan ilman edistystä ennen kuin
 * siirto katsotaan jumiutuneeksi. */
#define ODOTUSRAJA 100000u

// @alku kello
/* SCK = SSPCLK / (CPSDVSR * (1 + SCR)), CPSDVSR parillinen 2..254 ja
 * SCR 0..255. Haetaan pienin jakaja, joka ei ylitä haluttua
 * taajuutta. */
spi_tila_t pl022_kello(uint32_t sspclk, uint32_t haluttu,
                       pl022_kello_t *kello) {
    if (haluttu == 0) {
        return SPI_PARAMETRI;
    }
    uint32_t paras = 0;
    for (uint32_t esi = 2; esi <= 254; esi += 2) {
        /* pienin (1 + SCR), jolla esi * (1 + SCR) * haluttu >= sspclk */
        uint64_t askel = (uint64_t)esi * haluttu;
        uint64_t jakaja = (sspclk + askel - 1) / askel;
        if (jakaja > 256) {
            continue;
        }
        if (paras == 0 || esi * jakaja < paras) {
            paras = esi * (uint32_t)jakaja;
            kello->cpsdvsr = (uint8_t)esi;
            kello->scr = (uint8_t)(jakaja - 1);
        }
    }
    if (paras == 0) {
        return SPI_PARAMETRI;
    }
    kello->taajuus = sspclk / paras;
    return SPI_OK;
}
// @loppu kello

// @alku alusta
spi_tila_t pl022_alusta(pl022_t *spi, uint32_t sspclk, uint32_t haluttu,
                        unsigned moodi, unsigned bitit) {
    pl022_kello_t kello;
    if (moodi > 3 || bitit < 4 || bitit > 16 ||
        pl022_kello(sspclk, haluttu, &kello) != SPI_OK) {
        return SPI_PARAMETRI;
    }
    spi->CR1 = 0; /* asetukset muutetaan lohkon ollessa pois päältä */
    spi->CPSR = kello.cpsdvsr;
    spi->CR0 = PL022_CR0_DSS(bitit) | PL022_CR0_SCR(kello.scr) |
               ((moodi & 2u) ? PL022_CR0_SPO : 0) |
               ((moodi & 1u) ? PL022_CR0_SPH : 0);
    spi->CR1 = PL022_CR1_SSE; /* isäntä, normaali tila */
    return SPI_OK;
}
// @loppu alusta

// @alku siirto
spi_tila_t pl022_siirto(pl022_t *spi, const uint8_t *tx, uint8_t *rx,
                        size_t n) {
    size_t lahetetty = 0;
    size_t vastaanotettu = 0;
    unsigned odotus = 0;
    while (vastaanotettu < n) {
        int edistyi = 0;
        /* Täytetään lähetys-FIFO, mutta enintään FIFOn verran
         * kehyksiä matkalle: muuten vastaanotto-FIFO vuotaisi yli. */
        while (lahetetty < n && lahetetty - vastaanotettu < FIFO &&
               (spi->SR & PL022_SR_TNF)) {
            spi->DR = tx ? tx[lahetetty] : 0xFFu;
            lahetetty++;
            edistyi = 1;
        }
        while (vastaanotettu < lahetetty && (spi->SR & PL022_SR_RNE)) {
            uint8_t tavu = (uint8_t)spi->DR;
            if (rx) {
                rx[vastaanotettu] = tavu;
            }
            vastaanotettu++;
            edistyi = 1;
        }
        odotus = edistyi ? 0 : odotus + 1;
        if (odotus == ODOTUSRAJA) {
            return SPI_AIKARAJA;
        }
    }
    return SPI_OK;
}
// @loppu siirto
