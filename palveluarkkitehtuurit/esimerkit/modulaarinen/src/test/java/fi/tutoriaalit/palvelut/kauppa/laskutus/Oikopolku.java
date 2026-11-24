package fi.tutoriaalit.palvelut.kauppa.laskutus;

import fi.tutoriaalit.palvelut.kauppa.varasto.sisainen.SaldoTaulu;

/** Tahallinen rajarikkomus testiä varten: laskutus lukee varaston
 *  sisäistä taulua sen julkisen rajapinnan ohi. */
public class Oikopolku {
    int saldo(SaldoTaulu taulu) {
        return taulu.saldo("kahvinkeitin");
    }
}
