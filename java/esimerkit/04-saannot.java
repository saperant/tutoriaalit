import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.function.Function;
import java.util.function.Predicate;

/** Validointisäännöt datana: lambdat, metodiviittaukset ja sulkeumat. */
final class Main {
    private Main() {
    }

    // @alku tehdas
    /** Palauttaa säännön, joka sulkee sisäänsä parametrin pituus. */
    static Predicate<String> enintaan(int pituus) {
        return s -> s.length() <= pituus;
    }
    // @loppu tehdas

    // @alku saannot
    static final Map<String, Predicate<String>> SAANNOT;

    static {
        Map<String, Predicate<String>> s = new LinkedHashMap<>();
        s.put("ei tyhjä", Predicate.not(String::isBlank));
        s.put("enintään 12 merkkiä", enintaan(12));
        s.put("vain kirjaimia ja numeroita",
                t -> t.chars().allMatch(Character::isLetterOrDigit));
        SAANNOT = Map.copyOf(s);
    }

    static List<String> rikotut(String tunnus) {
        List<String> tulos = new ArrayList<>();
        SAANNOT.forEach((nimi, saanto) -> {
            if (!saanto.test(tunnus)) {
                tulos.add(nimi);
            }
        });
        tulos.sort(null);
        return tulos;
    }
    // @loppu saannot

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku kaytto
        Function<String, String> siisti = String::strip;
        Function<String, String> esikasittely =
                siisti.andThen(s -> s.toLowerCase(Locale.ROOT));
        for (String syote : List.of("  Maija77 ", "maija.virtanen", " ")) {
            String tunnus = esikasittely.apply(syote);
            List<String> virheet = rikotut(tunnus);
            System.out.printf("'%s': %s%n", tunnus,
                    virheet.isEmpty() ? "kelpaa" : virheet);
        }
        // @loppu kaytto
    }
}
