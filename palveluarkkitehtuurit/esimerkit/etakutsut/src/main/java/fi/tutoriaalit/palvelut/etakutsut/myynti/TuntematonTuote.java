package fi.tutoriaalit.palvelut.etakutsut.myynti;

/** Pysyvä virhe: uusi yritys ei auta. */
public class TuntematonTuote extends RuntimeException {
    public TuntematonTuote(String tuote) {
        super("tuntematon tuote: " + tuote);
    }
}
