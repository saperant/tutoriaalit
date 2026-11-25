import java.util.ArrayList;
import java.util.List;

/** Rajapinta, oletusmetodi ja koristelija (decorator) periytymisen sijaan. */
final class Main {
    private Main() {
    }

    // @alku rajapinta
    /** Tuotteen hinta sentteinä asiakkaalle. */
    @FunctionalInterface
    interface Hinnoittelu {
        long hinta(String tuote, int maara);

        default Hinnoittelu alennus(int prosenttia) {
            return (t, m) -> hinta(t, m) * (100 - prosenttia) / 100;
        }
    }
    // @loppu rajapinta

    // @alku koristelija
    /** Kirjaa jokaisen kutsun ja delegoi varsinaiselle toteutukselle. */
    static final class Kirjaava implements Hinnoittelu {
        private final Hinnoittelu sisempi;
        private final List<String> loki;

        Kirjaava(Hinnoittelu sisempi, List<String> loki) {
            this.sisempi = sisempi;
            this.loki = loki;
        }

        @Override
        public long hinta(String tuote, int maara) {
            long h = sisempi.hinta(tuote, maara);
            loki.add(tuote + " x" + maara + " = " + h);
            return h;
        }
    }
    // @loppu koristelija

    public static void main(String[] args) {
        // @alku kaytto
        Hinnoittelu perus = (tuote, maara) -> switch (tuote) {
            case "kahvi" -> 695L * maara;
            case "tee" -> 450L * maara;
            default -> throw new IllegalArgumentException(tuote);
        };
        List<String> loki = new ArrayList<>();
        Hinnoittelu kanta = new Kirjaava(perus.alennus(10), loki);
        System.out.println(kanta.hinta("kahvi", 3) + kanta.hinta("tee", 2));
        loki.forEach(System.out::println);
        // @loppu kaytto
    }
}
