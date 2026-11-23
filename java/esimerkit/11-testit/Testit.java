import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/** Minimaalinen testiajuri: sama rakenne kuin JUnitissa. */
final class Testit {
    /** Testi, joka voi heittää minkä tahansa poikkeuksen. */
    @FunctionalInterface
    interface Testi {
        void aja() throws Exception;
    }

    private record Tapaus(String nimi, Testi testi) {
    }

    private final List<Tapaus> tapaukset = new ArrayList<>();

    void testi(String nimi, Testi testi) {
        tapaukset.add(new Tapaus(nimi, testi));
    }

    static void oletaYhtasuuri(Object odotettu, Object saatu) {
        if (!Objects.equals(odotettu, saatu)) {
            throw new AssertionError("odotettiin " + odotettu
                    + ", saatiin " + saatu);
        }
    }

    static <T extends Throwable> T oletaPoikkeus(Class<T> tyyppi,
            Testi testi) {
        try {
            testi.aja();
        } catch (Throwable t) {
            if (tyyppi.isInstance(t)) {
                return tyyppi.cast(t);
            }
            throw new AssertionError("väärä poikkeus: " + t, t);
        }
        throw new AssertionError("odotettiin " + tyyppi.getSimpleName());
    }

    /** Ajaa kaikki testit; palauttaa epäonnistuneiden määrän. */
    int ajaKaikki() {
        int epaonnistui = 0;
        for (Tapaus t : tapaukset) {
            try {
                t.testi().aja();
                System.out.println("OK    " + t.nimi());
            } catch (Exception | AssertionError e) {
                epaonnistui++;
                System.out.println("VIRHE " + t.nimi() + ": "
                        + e.getMessage());
            }
        }
        System.out.printf("%d testiä, %d epäonnistui%n", tapaukset.size(),
                epaonnistui);
        return epaonnistui;
    }
}
