/* SPI-väylän A/D-muunnin MAX1111 (8 bittiä, 4 kanavaa, sisäinen
 * 2,048 V:n referenssi). QEMU antaa kanavien jännitteet
 * komentoriviltä (ks. Makefile). */
#include <stddef.h>
#include <stdint.h>

#include "konsoli.h"
#include "mps2.h"
#include "pl022.h"

// @alku ohjaustavu
/* Ohjaustavu: START, kanava (SEL2..SEL0), UNI/BIP, SGL/DIF, PD1,
 * PD0. Kanavan valintabitit eivät ole suora binääriluku, joten ajuri
 * käyttää datalehden taulukkoa. */
#define MAX1111_START (1u << 7)
#define MAX1111_UNI   (1u << 3) /* yksinapainen: 0..Vref */
#define MAX1111_SGL   (1u << 2) /* maata vasten, ei erotus */
#define MAX1111_PD    (3u << 0) /* ulkoinen kello, ei virransäästöä */

static const uint8_t kanavan_sel[4] = {0x1, 0x5, 0x3, 0x7};
// @loppu ohjaustavu

// @alku muunnos
typedef struct {
    pl022_t *spi;
    unsigned vref_mv;
} max1111_t;

/* Yksi muunnos on kolmen tavun siirto: ohjaustavu ja kaksi tyhjää
 * tavua, joiden aikana tulos siirtyy ulos. Tuloksen kahdeksan bittiä
 * jakautuvat tavujen rajan yli: 00XXXXXX XX000000. */
static spi_tila_t max1111_lue(const max1111_t *a, unsigned kanava,
                              uint8_t *koodi) {
    if (kanava >= sizeof kanavan_sel) {
        return SPI_PARAMETRI;
    }
    const uint8_t tx[3] = {
        (uint8_t)(MAX1111_START | kanavan_sel[kanava] << 4 |
                  MAX1111_UNI | MAX1111_SGL | MAX1111_PD),
        0, 0};
    uint8_t rx[3];
    spi_tila_t tila = pl022_siirto(a->spi, tx, rx, sizeof tx);
    if (tila == SPI_OK) {
        *koodi = (uint8_t)((rx[1] & 0x3Fu) << 2 | rx[2] >> 6);
    }
    return tila;
}

static unsigned millivolteiksi(const max1111_t *a, uint8_t koodi) {
    return (koodi * a->vref_mv + 128u) / 256u; /* pyöristys */
}
// @loppu muunnos

// @alku itsetesti
/* Silmukkatilassa (LBM) lähetys kytkeytyy lohkon sisällä suoraan
 * vastaanottoon. Testi todistaa ajurin ja FIFOjen toimivan ennen
 * kuin yhtäkään laitetta on kytketty. */
static int itsetesti(pl022_t *spi) {
    static const uint8_t malli[] = {0x00, 0xFF, 0xA5, 0x5A, 0x01,
                                    0x80, 0x3C, 0xC3, 0x77, 0x88,
                                    0x12, 0x34};
    uint8_t takaisin[sizeof malli];
    spi->CR1 |= PL022_CR1_LBM;
    spi_tila_t tila = pl022_siirto(spi, malli, takaisin, sizeof malli);
    spi->CR1 &= ~PL022_CR1_LBM;
    if (tila != SPI_OK) {
        return 0;
    }
    for (size_t i = 0; i < sizeof malli; i++) {
        if (takaisin[i] != malli[i]) {
            return 0;
        }
    }
    return 1;
}
// @loppu itsetesti

// @alku main
int main(void) {
    konsoli_alusta();
    pl022_kello_t kello;
    if (pl022_kello(KELLO_HZ, 1000000u, &kello) != SPI_OK ||
        pl022_alusta(SPI_ADC, KELLO_HZ, 1000000u, 0, 8) != SPI_OK) {
        tulosta("SPI:n alustus epaonnistui\n");
        return 1;
    }
    tulosta("SCK %u Hz (CPSDVSR %u, SCR %u), moodi 0\n",
            (unsigned)kello.taajuus, kello.cpsdvsr, kello.scr);
    if (!itsetesti(SPI_ADC)) {
        tulosta("itsetesti epaonnistui\n");
        return 1;
    }
    tulosta("itsetesti ok: 12 tavua silmukan kautta\n");

    const max1111_t adc = {SPI_ADC, 2048};
    for (unsigned kanava = 0; kanava < 4; kanava++) {
        uint8_t koodi;
        if (max1111_lue(&adc, kanava, &koodi) != SPI_OK) {
            tulosta("kanava %u: aikaraja\n", kanava);
            return 1;
        }
        tulosta("kanava %u: koodi %3u = %4u mV\n", kanava, koodi,
                millivolteiksi(&adc, koodi));
    }
    return 0;
}
// @loppu main
