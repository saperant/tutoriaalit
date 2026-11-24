package fi.tutoriaalit.kauppa.virheet;

/** Pyydettyä resurssia ei ole. Rajapinnassa 404 Not Found. */
public class EiLoydy extends RuntimeException {

    public EiLoydy(String mita, Object tunniste) {
        super(mita + " " + tunniste + " ei löydy");
    }
}
