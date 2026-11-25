import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/** Optional paluuarvona: puuttuva arvo osana rajapintaa. */
final class Main {
    record Asiakas(String tunnus, String nimi, String alennuskoodi) {
    }

    static final List<Asiakas> ASIAKKAAT = List.of(
            new Asiakas("A1", "Maija", "KESÄ10"),
            new Asiakas("A2", "Pekka", null));
    static final Map<String, Integer> ALENNUKSET = Map.of("KESÄ10", 10);

    private Main() {
    }

    // @alku haku
    static Optional<Asiakas> hae(String tunnus) {
        return ASIAKKAAT.stream()
                .filter(a -> a.tunnus().equals(tunnus))
                .findFirst();
    }

    static int alennusProsentti(String tunnus) {
        return hae(tunnus)
                .map(Asiakas::alennuskoodi)       // null -> tyhjä
                .map(ALENNUKSET::get)
                .orElse(0);
    }
    // @loppu haku

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku kaytto
        for (String t : List.of("A1", "A2", "A9")) {
            System.out.println(t + ": " + alennusProsentti(t) + " %");
        }
        String nimi = hae("A1").map(Asiakas::nimi).orElseThrow();
        System.out.println(nimi);
        hae("A9").ifPresentOrElse(
                a -> System.out.println("löytyi " + a.nimi()),
                () -> System.out.println("A9 ei ole asiakas"));
        // @loppu kaytto
    }
}
