package fi.tutoriaalit.kauppa.virheet;

/** Tilaus ei mahdu varastoon. Rajapinnassa 409 Conflict. */
public class SaldoEiRiita extends RuntimeException {

    private final long tuoteId;
    private final int pyydetty;

    public SaldoEiRiita(long tuoteId, int pyydetty) {
        super("tuotteen " + tuoteId + " saldo ei riitä");
        this.tuoteId = tuoteId;
        this.pyydetty = pyydetty;
    }

    public long tuoteId() {
        return tuoteId;
    }

    public int pyydetty() {
        return pyydetty;
    }
}
