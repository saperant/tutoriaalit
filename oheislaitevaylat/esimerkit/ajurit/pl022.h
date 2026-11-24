/* PL022-SPI-isännän ajuri: pollaava siirto FIFOjen kautta. */
#ifndef PL022_H
#define PL022_H

#include <stddef.h>
#include <stdint.h>

#include "mps2.h"

// @alku rajapinta
typedef enum {
    SPI_OK = 0,
    SPI_PARAMETRI, /* taajuus, moodi tai sanan koko ei kelpaa */
    SPI_AIKARAJA,  /* FIFO ei edennyt odotusrajan aikana */
} spi_tila_t;

typedef struct {
    uint32_t taajuus; /* toteutunut SCK-taajuus, Hz */
    uint8_t cpsdvsr;  /* esijakaja */
    uint8_t scr;      /* kellon jakaja - 1 */
} pl022_kello_t;

/* Laskee jakajat niin, että SCK on enintään haluttu taajuus. */
spi_tila_t pl022_kello(uint32_t sspclk, uint32_t haluttu,
                       pl022_kello_t *kello);

/* moodi 0..3 = CPOL * 2 + CPHA, bitit 4..16. */
spi_tila_t pl022_alusta(pl022_t *spi, uint32_t sspclk, uint32_t haluttu,
                        unsigned moodi, unsigned bitit);

/* Kaksisuuntainen siirto: lähettää n tavua tx:stä ja tallentaa
 * samaan aikaan vastaanotetut rx:ään. tx tai rx voi olla NULL. */
spi_tila_t pl022_siirto(pl022_t *spi, const uint8_t *tx, uint8_t *rx,
                        size_t n);
// @loppu rajapinta

#endif
