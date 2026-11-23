import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.util.List;

/** Suljettu tyyppihierarkia ja kuvioiden sovitus switchissä. */
final class Main {
    private Main() {
    }

    // @alku tyypit
    sealed interface Maksu permits Kortti, Lasku, Lahjakortti {
        long senttia();
    }

    record Kortti(long senttia, String verkko) implements Maksu {
    }

    record Lasku(long senttia, int maksuaikaPv) implements Maksu {
    }

    record Lahjakortti(long senttia, String koodi) implements Maksu {
    }
    // @loppu tyypit

    // @alku kulut
    /** Maksun käsittelykulu sentteinä. */
    static long kulu(Maksu maksu) {
        return switch (maksu) {
            case Kortti(long s, String verkko) when verkko.equals("Amex") ->
                    s * 3 / 100;
            case Kortti k -> k.senttia() / 100 + 10;
            case Lasku(long s, int pv) when pv > 30 -> 500;
            case Lasku l -> 250;
            case Lahjakortti g -> 0;
        };
    }
    // @loppu kulut

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku kaytto
        List<Maksu> maksut = List.of(
                new Kortti(10_000, "Visa"),
                new Kortti(10_000, "Amex"),
                new Lasku(25_000, 14),
                new Lasku(25_000, 60),
                new Lahjakortti(5_000, "LK-77"));
        for (Maksu m : maksut) {
            System.out.printf("%-38s kulu %3d snt%n", m, kulu(m));
        }
        // @loppu kaytto
    }
}
