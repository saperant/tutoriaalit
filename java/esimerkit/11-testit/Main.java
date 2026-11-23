import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;

/** Toimitusmaksun testit. */
final class Main {
    private Main() {
    }

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        var t = new Testit();
        t.testi("perusmaksu mantereelle", () ->
                Testit.oletaYhtasuuri(590, Toimitus.maksu("manner", 800, 0)));
        t.testi("ilmainen toimitus rajalla", () ->
                Testit.oletaYhtasuuri(0, Toimitus.maksu("manner", 800,
                        Toimitus.ILMAINEN_ALKAEN_SNT)));
        t.testi("lisäkilot yli 5 kg", () -> {
            Testit.oletaYhtasuuri(590, Toimitus.maksu("manner", 5000, 0));
            Testit.oletaYhtasuuri(690, Toimitus.maksu("manner", 5001, 0));
            Testit.oletaYhtasuuri(1290,
                    Toimitus.maksu("ahvenanmaa", 7500, 0));
        });
        t.testi("raskas ei ole koskaan ilmainen", () ->
                Testit.oletaYhtasuuri(2190, Toimitus.maksu("manner", 20_001,
                        9_999)));
        t.testi("tuntematon alue", () -> {
            var e = Testit.oletaPoikkeus(IllegalArgumentException.class,
                    () -> Toimitus.maksu("kuu", 100, 0));
            Testit.oletaYhtasuuri("tuntematon alue: kuu", e.getMessage());
        });
        if (t.ajaKaikki() != 0) {
            System.exit(1);
        }
    }
}
