/* Keskeytysohjattu lähetys: ohjelma kirjoittaa tekstin renkaaseen ja
 * jatkaa työtään, ja UART0:n lähetyskeskeytys siirtää tavut
 * renkaasta lähettimeen sitä mukaa kuin lähetysrekisteri vapautuu.
 *
 * Makrolla ILMAN_KAYNNISTYSTA käännetty versio näyttää yleisen
 * virheen: keskeytys sallitaan, mutta lähetystä ei käynnistetä. */
#include <stddef.h>
#include <stdint.h>

#include "konsoli.h"
#include "mps2.h"
#include "rengas.h"

static rengas_t lahtevat;

// @alku keskeytys
void UART0TX_IRQHandler(void) {
    UART0->INTSTATUS = UART_INT_TX; /* kuittaus ennen uutta tavua */
    uint8_t tavu;
    if (rengas_ota(&lahtevat, &tavu)) {
        UART0->DATA = tavu;
    } else {
        /* Ei lähetettävää: keskeytys pois, muuten se toistuisi. */
        UART0->CTRL &= ~UART_CTRL_TXINTEN;
    }
}
// @loppu keskeytys

// @alku kaynnista
/* CMSDK:n UART keskeyttää vasta, kun lähetysrekisteri tyhjenee.
 * Joutilas lähetin ei siis keskeytä koskaan, joten ensimmäinen tavu
 * kirjoitetaan itse, ja vasta kun keskeytys on sallittu: muuten
 * tyhjeneminen ehtisi tapahtua ennen sallimista ja menisi ohi.
 * Kutsutaan keskeytykset kiellettyinä, jottei käsittelijä ehdi
 * poistaa TXINTEN-bittiä kesken kaiken. */
static void kaynnista(void) {
    if (UART0->CTRL & UART_CTRL_TXINTEN) {
        return; /* lähetys on jo käynnissä */
    }
    UART0->CTRL |= UART_CTRL_TXINTEN;
#ifndef ILMAN_KAYNNISTYSTA
    uint8_t tavu;
    if (rengas_ota(&lahtevat, &tavu)) {
        UART0->DATA = tavu;
    }
#endif
}
// @loppu kaynnista

// @alku kirjoita
/* Kirjoittaa tekstin lähetysjonoon. Jos rengas on täynnä, odotetaan
 * enintään raja kierrosta, että keskeytys vapauttaa tilaa.
 * Palauttaa jonoon päässeiden tavujen määrän. */
static size_t uart_kirjoita(const char *teksti, uint32_t raja) {
    size_t kirjoitettu = 0;
    uint32_t odotus = 0;
    while (teksti[kirjoitettu] != '\0' && odotus < raja) {
        uint32_t primask = lue_primask();
        keskeytykset_pois();
        int mahtui = rengas_lisaa(&lahtevat, (uint8_t)teksti[kirjoitettu]);
        kaynnista();
        aseta_primask(primask);
        if (mahtui) {
            kirjoitettu++;
            odotus = 0;
        } else {
            odotus++;
        }
    }
    return kirjoitettu;
}
// @loppu kirjoita

static int jono_tyhja(uint32_t raja) {
    for (uint32_t kierros = 0; kierros < raja; kierros++) {
        if (lahtevat.kirjoitus == lahtevat.luku) {
            return 1;
        }
    }
    return 0;
}

// @alku main
static const char raportti[] =
    "Mittausraportti\n"
    "  kanava 1: 1016 mV\n"
    "  kanava 2: 1600 mV\n"
    "  kanava 3: 2040 mV\n"
    "Raportti on pidempi kuin 64 tavun rengas, joten kirjoittaja\n"
    "odottaa valilla, etta keskeytys tyhjentaa tilaa.\n";

int main(void) {
    konsoli_alusta();
    nvic_salli(UART0TX_IRQn);
    size_t jonoon = uart_kirjoita(raportti, 1000000u);
    if (jonoon < sizeof raportti - 1 || !jono_tyhja(1000000u)) {
        UART0->CTRL &= ~UART_CTRL_TXINTEN; /* pollaava konsoli */
        tulosta("lahetys ei edennyt: jonoon %u/%u tavua\n",
                (unsigned)jonoon, (unsigned)(sizeof raportti - 1));
        return 1;
    }
    tulosta("valmis: %u tavua keskeytyksilla\n", (unsigned)jonoon);
    return 0;
}
// @loppu main
