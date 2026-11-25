import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Objects;

/** Rakentaja (builder) monen valinnaisen kentän muuttumattomalle oliolle. */
final class Main {
    private Main() {
    }

    // @alku pyynto
    record Pyynto(String metodi, String osoite, Map<String, String> otsakkeet,
            Duration aikaraja, int yrityksia) {

        Pyynto {
            otsakkeet = Map.copyOf(otsakkeet); // puolustava kopio
        }

        static Rakentaja get(String osoite) {
            return new Rakentaja("GET", osoite);
        }

        static final class Rakentaja {
            private final String metodi;
            private final String osoite;
            private final Map<String, String> otsakkeet =
                    new LinkedHashMap<>();
            private Duration aikaraja = Duration.ofSeconds(10);
            private int yrityksia = 1;

            private Rakentaja(String metodi, String osoite) {
                this.metodi = metodi;
                this.osoite = Objects.requireNonNull(osoite, "osoite");
            }

            Rakentaja otsake(String nimi, String arvo) {
                otsakkeet.put(nimi, arvo);
                return this;
            }

            Rakentaja aikaraja(Duration aika) {
                if (aika.isNegative() || aika.isZero()) {
                    throw new IllegalArgumentException("aikaraja <= 0");
                }
                this.aikaraja = aika;
                return this;
            }

            Rakentaja yrityksia(int maara) {
                this.yrityksia = maara;
                return this;
            }

            Pyynto rakenna() {
                if (yrityksia < 1 || yrityksia > 5) {
                    throw new IllegalStateException("yrityksiä 1..5");
                }
                return new Pyynto(metodi, osoite, otsakkeet, aikaraja,
                        yrityksia);
            }
        }
    }
    // @loppu pyynto

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku kaytto
        Pyynto p = Pyynto.get("https://api.example.com/tilaukset")
                .otsake("Accept", "application/json")
                .aikaraja(Duration.ofSeconds(2))
                .yrityksia(3)
                .rakenna();
        System.out.println(p.metodi() + " " + p.osoite());
        System.out.println(p.otsakkeet() + ", " + p.aikaraja() + ", "
                + p.yrityksia() + " yritystä");
        // @loppu kaytto
    }
}
