package fi.esimerkki.tilaus;

/** Tehdasmetodit varastototeutuksille. */
public final class Varastot {
    private Varastot() {
    }

    public static Varasto muistiin() {
        return new MuistiVarasto();
    }
}
