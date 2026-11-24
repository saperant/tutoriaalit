package fi.tutoriaalit.palvelut.kauppa.varasto.sisainen;

import fi.tutoriaalit.palvelut.kauppa.myynti.TilausTehty;
import fi.tutoriaalit.palvelut.kauppa.varasto.SaldoEiRiita;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

// @alku varaus
/** Varaa tuotteet tilaukselle samassa transaktiossa kuin tilaus
 *  tallennetaan. Jos saldo ei riitä, koko tilaus perutaan. */
@Component
class VarausKuuntelija {
    private final SaldoTaulu taulu;

    VarausKuuntelija(SaldoTaulu taulu) {
        this.taulu = taulu;
    }

    @EventListener
    void kunTilausTehty(TilausTehty tilaus) {
        if (!taulu.vahenna(tilaus.tuote(), tilaus.maara())) {
            throw new SaldoEiRiita(tilaus.tuote());
        }
    }
}
// @loppu varaus
