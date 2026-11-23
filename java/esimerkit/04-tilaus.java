import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.util.List;

/** Tilauksen tilakone enum-tyypillä ja switch-lausekkeella. */
final class Main {
    // @alku tyypit
    enum Tila { AVOIN, MAKSETTU, LAHETETTY, PERUTTU }

    enum Tapahtuma { MAKSU, LAHETYS, PERUUTUS }

    static Tila seuraava(Tila tila, Tapahtuma tapahtuma) {
        return switch (tila) {
            case AVOIN -> switch (tapahtuma) {
                case MAKSU -> Tila.MAKSETTU;
                case PERUUTUS -> Tila.PERUTTU;
                case LAHETYS -> throw virhe(tila, tapahtuma);
            };
            case MAKSETTU -> switch (tapahtuma) {
                case LAHETYS -> Tila.LAHETETTY;
                case PERUUTUS -> Tila.PERUTTU;
                case MAKSU -> throw virhe(tila, tapahtuma);
            };
            case LAHETETTY, PERUTTU -> throw virhe(tila, tapahtuma);
        };
    }

    static IllegalStateException virhe(Tila tila, Tapahtuma t) {
        return new IllegalStateException(t + " ei sallittu tilassa " + tila);
    }
    // @loppu tyypit

    private Main() {
    }

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku kaytto
        List<List<Tapahtuma>> kulut = List.of(
                List.of(Tapahtuma.MAKSU, Tapahtuma.LAHETYS),
                List.of(Tapahtuma.PERUUTUS),
                List.of(Tapahtuma.LAHETYS));
        for (List<Tapahtuma> kulku : kulut) {
            Tila tila = Tila.AVOIN;
            try {
                for (Tapahtuma t : kulku) {
                    tila = seuraava(tila, t);
                }
                System.out.println(kulku + " -> " + tila);
            } catch (IllegalStateException e) {
                System.out.println(kulku + " -> virhe: " + e.getMessage());
            }
        }
        // @loppu kaytto
    }
}
