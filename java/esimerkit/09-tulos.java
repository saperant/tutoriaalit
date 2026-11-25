import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.util.ArrayList;
import java.util.List;

/** Odotettavat virheet tulostyyppinä: kaikki virheet kerralla. */
final class Main {
    private Main() {
    }

    // @alku tulos
    sealed interface Tulos<T> {
        record Ok<T>(T arvo) implements Tulos<T> {
        }

        record Virheet<T>(List<String> viestit) implements Tulos<T> {
        }
    }

    record Rekisterointi(String sahkoposti, int ika) {
    }

    static Tulos<Rekisterointi> tarkista(String sahkoposti, String ika) {
        List<String> virheet = new ArrayList<>();
        if (!sahkoposti.matches("[^@\\s]+@[^@\\s]+\\.[a-z]{2,}")) {
            virheet.add("sähköposti on virheellinen");
        }
        int vuodet = -1;
        try {
            vuodet = Integer.parseInt(ika);
        } catch (NumberFormatException e) {
            virheet.add("ikä ei ole luku");
        }
        if (vuodet != -1 && (vuodet < 13 || vuodet > 120)) {
            virheet.add("iän on oltava 13–120");
        }
        return virheet.isEmpty()
                ? new Tulos.Ok<>(new Rekisterointi(sahkoposti, vuodet))
                : new Tulos.Virheet<>(List.copyOf(virheet));
    }
    // @loppu tulos

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku kaytto
        String[][] syotteet = {
            {"maija@example.com", "34"},
            {"pekka(at)example", "9"},
            {"liisa@example.fi", "kolme"},
        };
        for (String[] s : syotteet) {
            String viesti = switch (tarkista(s[0], s[1])) {
                case Tulos.Ok<Rekisterointi>(var r) -> "ok: " + r;
                case Tulos.Virheet<Rekisterointi>(var v) ->
                        "hylätty: " + String.join("; ", v);
            };
            System.out.println(viesti);
        }
        // @loppu kaytto
    }
}
