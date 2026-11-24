package fi.tutoriaalit.kauppa.virheet;

/** Pyyntö on muodoltaan oikein mutta sisällöltään virheellinen (400). */
public class VirheellinenPyynto extends RuntimeException {

    public VirheellinenPyynto(String syy) {
        super(syy);
    }
}
