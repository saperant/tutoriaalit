/* Kehysprotokolla UART1:n yli. Isäntä lähettää komentokehyksiä, ja
 * laite vastaa jokaiseen kehykseen. Vastaanottokeskeytys siirtää
 * tavut renkaaseen; pääsilmukka kokoaa ne kehyksiksi erottimeen
 * 0x00 asti, purkaa COBSin ja tarkistaa CRC:n.
 *
 * QEMU syöttää isännän tavut tiedostosta ja kirjoittaa vastaukset
 * toiseen tiedostoon; molemmat tuottaa ja tarkistaa Python-malli. */
#include <stddef.h>
#include <stdint.h>

#include "kehys.h"
#include "konsoli.h"
#include "mps2.h"
#include "rengas.h"

enum {
    KOMENTO_KAIKU = 0x01,
    KOMENTO_SUMMA = 0x02,
    KOMENTO_LOPPU = 0x7F,
    VASTAUS = 0x80,   /* vastauksessa komennon ylin bitti asetettu */
    KIELTEINEN = 0xEE, /* NAK: syykoodi perässä */
};

enum { SYY_CRC = 1, SYY_COBS = 2, SYY_PITUUS = 3, SYY_KOMENTO = 4 };

#define KUORMA_MAX 32u /* hyötykuorman enimmäispituus ilman CRC:tä */

// @alku vastaanotto
static rengas_t saapuvat;

static int taynna(const rengas_t *r) {
    return r->kirjoitus - r->luku == RENGAS_KOKO;
}

void UART1RX_IRQHandler(void) {
    /* Kuittaus ensin, sitten tyhjennys: jos tavu saapuu tyhjennyksen
     * jälkeen, keskeytys asettuu uudelleen eikä tavu jää odottamaan. */
    UART1->INTSTATUS = UART_INT_RX;
    while (UART1->STATE & UART_STATE_RXFULL) {
        if (taynna(&saapuvat)) {
            /* Vuonohjaus: tavu jätetään vastaanottimeen, jolloin
             * seuraava ei mahdu linjalta sisään. Keskeytys pois,
             * kunnes pääsilmukka on vapauttanut tilaa. */
            UART1->CTRL &= ~UART_CTRL_RXINTEN;
            return;
        }
        (void)rengas_lisaa(&saapuvat, (uint8_t)UART1->DATA);
    }
}

static uint8_t lue_tavu(void) {
    uint8_t tavu;
    while (!rengas_ota(&saapuvat, &tavu)) {
        /* Odotetaan. Oikeassa laitteessa tässä olisi aikaraja tai
         * lepotila (ks. Mikrokontrollerit, luku 8). */
    }
    uint32_t primask = lue_primask();
    keskeytykset_pois();
    if (!(UART1->CTRL & UART_CTRL_RXINTEN)) {
        /* Tilaa vapautui: keskeytys takaisin päälle ja käsittelijä
         * ajoon, sillä vastaanottimessa odottaa jo tavu, eikä sen
         * keskeytys toistu itsestään. */
        UART1->CTRL |= UART_CTRL_RXINTEN;
        nvic_laukaise(UART1RX_IRQn);
    }
    aseta_primask(primask);
    return tavu;
}
// @loppu vastaanotto

// @alku laheta
static void uart1_merkki(uint8_t tavu) {
    while (UART1->STATE & UART_STATE_TXFULL) {
    }
    UART1->DATA = tavu;
}

static void laheta_kehys(const uint8_t *data, size_t n) {
    uint8_t kuorma[KUORMA_MAX + 2];
    uint8_t koodattu[sizeof kuorma + 1];
    for (size_t i = 0; i < n; i++) {
        kuorma[i] = data[i];
    }
    uint16_t crc = crc16(data, n);
    kuorma[n] = (uint8_t)(crc >> 8);
    kuorma[n + 1] = (uint8_t)crc;
    size_t pituus = cobs_koodaa(kuorma, n + 2, koodattu);
    for (size_t i = 0; i < pituus; i++) {
        uart1_merkki(koodattu[i]);
    }
    uart1_merkki(KEHYS_EROTIN);
}

static void hylkaa(uint8_t syy) {
    const uint8_t nak[] = {KIELTEINEN, syy};
    laheta_kehys(nak, sizeof nak);
}
// @loppu laheta

// @alku kasittele
/* Käsittelee yhden puretun kehyksen. Palauttaa 0, kun isäntä
 * lopettaa istunnon. */
static int kasittele(const uint8_t *kuorma, size_t n) {
    uint8_t vastaus[KUORMA_MAX];
    vastaus[0] = (uint8_t)(kuorma[0] | VASTAUS);
    switch (kuorma[0]) {
    case KOMENTO_KAIKU:
        tulosta("kaiku, %u tavua\n", (unsigned)(n - 1));
        for (size_t i = 1; i < n; i++) {
            vastaus[i] = kuorma[i];
        }
        laheta_kehys(vastaus, n);
        return 1;
    case KOMENTO_SUMMA: {
        unsigned summa = 0;
        for (size_t i = 1; i < n; i++) {
            summa += kuorma[i];
        }
        tulosta("summa %u tavusta = %u\n", (unsigned)(n - 1), summa);
        vastaus[1] = (uint8_t)(summa >> 8);
        vastaus[2] = (uint8_t)summa;
        laheta_kehys(vastaus, 3);
        return 1;
    }
    case KOMENTO_LOPPU:
        tulosta("loppu\n");
        laheta_kehys(vastaus, 1);
        return 0;
    default:
        tulosta("tuntematon komento %02x\n", kuorma[0]);
        hylkaa(SYY_KOMENTO);
        return 1;
    }
}
// @loppu kasittele

// @alku main
int main(void) {
    konsoli_alusta();
    UART1->BAUDDIV = KELLO_HZ / 115200u;
    UART1->CTRL = UART_CTRL_TXEN | UART_CTRL_RXEN | UART_CTRL_RXINTEN;
    nvic_salli(UART1RX_IRQn);

    uint8_t kehys[KUORMA_MAX + 2 + 1]; /* COBS lisää yhden tavun */
    size_t pituus = 0;
    int ylipitka = 0;
    for (;;) {
        uint8_t tavu = lue_tavu();
        if (tavu != KEHYS_EROTIN) {
            /* Liian pitkä kehys luetaan erottimeen asti ja hylätään:
             * erotin on aina nolla, joten tahdistus palautuu. */
            if (pituus < sizeof kehys) {
                kehys[pituus++] = tavu;
            } else {
                ylipitka = 1;
            }
            continue;
        }
        int n = ylipitka ? -1 : cobs_pura(kehys, pituus);
        if (ylipitka) {
            tulosta("hylatty: liian pitka kehys\n");
            hylkaa(SYY_PITUUS);
        } else if (n < 0) {
            tulosta("hylatty: virheellinen COBS\n");
            hylkaa(SYY_COBS);
        } else if (n < 3) {
            tulosta("hylatty: liian lyhyt kehys\n");
            hylkaa(SYY_PITUUS);
        } else if (crc16(kehys, (size_t)n) != 0) {
            tulosta("hylatty: CRC ei tasmaa\n");
            hylkaa(SYY_CRC);
        } else if (!kasittele(kehys, (size_t)n - 2)) {
            return 0;
        }
        pituus = 0;
        ylipitka = 0;
    }
}
// @loppu main
