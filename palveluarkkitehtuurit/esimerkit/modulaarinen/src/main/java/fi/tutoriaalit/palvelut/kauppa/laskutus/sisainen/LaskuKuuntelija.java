package fi.tutoriaalit.palvelut.kauppa.laskutus.sisainen;

import fi.tutoriaalit.palvelut.kauppa.myynti.TilausTehty;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.event.TransactionalEventListener;

// @alku lasku
/** Laskuttaa vasta, kun tilaus on varmasti tallennettu. Kuuntelija
 *  ajetaan tilauksen transaktion jälkeen, joten se tarvitsee oman
 *  transaktionsa (REQUIRES_NEW), muuten sen kirjoitukset eivät
 *  tallennu. */
@Component
class LaskuKuuntelija {
    private final LaskuTaulu taulu;

    LaskuKuuntelija(LaskuTaulu taulu) {
        this.taulu = taulu;
    }

    @TransactionalEventListener
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    void kunTilausTehty(TilausTehty tilaus) {
        taulu.lisaa(tilaus.tilausId(), tilaus.asiakas());
    }
}
// @loppu lasku
