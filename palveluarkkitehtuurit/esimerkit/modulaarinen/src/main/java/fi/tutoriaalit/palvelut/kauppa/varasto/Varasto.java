package fi.tutoriaalit.palvelut.kauppa.varasto;

import fi.tutoriaalit.palvelut.kauppa.varasto.sisainen.SaldoTaulu;
import org.springframework.stereotype.Service;

/** Varaston julkinen rajapinta. */
@Service
public class Varasto {
    private final SaldoTaulu taulu;

    Varasto(SaldoTaulu taulu) {
        this.taulu = taulu;
    }

    public int saldo(String tuote) {
        return taulu.saldo(tuote);
    }
}
