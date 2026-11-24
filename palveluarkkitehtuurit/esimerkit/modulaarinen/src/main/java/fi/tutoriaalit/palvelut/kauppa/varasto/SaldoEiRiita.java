package fi.tutoriaalit.palvelut.kauppa.varasto;

/** Tuotetta ei ole tarpeeksi. */
public class SaldoEiRiita extends RuntimeException {
    public SaldoEiRiita(String tuote) {
        super("saldo ei riitä: " + tuote);
    }
}
