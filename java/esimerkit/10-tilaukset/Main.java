import fi.esimerkki.tilaus.TilausPalvelu;
import fi.esimerkki.tilaus.Varastot;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;

/** Kokoonpanon juuri: ainoa paikka, jossa toteutukset valitaan. */
final class Main {
    private Main() {
    }

    /** Testeissä ja esimerkissä aikaa siirretään käsin. */
    static final class SiirrettavaKello extends Clock {
        private Instant nyt;

        SiirrettavaKello(Instant alku) {
            this.nyt = alku;
        }

        void siirra(Duration d) {
            nyt = nyt.plus(d);
        }

        @Override
        public Instant instant() {
            return nyt;
        }

        @Override
        public ZoneId getZone() {
            return ZoneOffset.UTC;
        }

        @Override
        public Clock withZone(ZoneId zone) {
            throw new UnsupportedOperationException();
        }
    }

    public static void main(String[] args) {
        var kello = new SiirrettavaKello(
                Instant.parse("2026-11-23T08:00:00Z"));
        var palvelu = new TilausPalvelu(Varastot.muistiin(), kello);

        palvelu.luo("Maija", 2085);
        kello.siirra(Duration.ofHours(30));
        palvelu.luo("Pekka", 450);
        kello.siirra(Duration.ofHours(1));

        palvelu.vanhentuneet(Duration.ofDays(1))
                .forEach(t -> System.out.printf("vanha: %d %s %s%n",
                        t.numero(), t.asiakas(), t.luotu()));
    }
}
