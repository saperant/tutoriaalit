package fi.tutoriaalit.palvelut.etakutsut.myynti;

/** Ohimenevä virhe: aikakatkaisu, katkennut yhteys tai 5xx. */
public class PalveluEiVastaa extends RuntimeException {
    public PalveluEiVastaa(String viesti, Throwable syy) {
        super(viesti, syy);
    }
}
