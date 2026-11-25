import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.io.Serial;
import java.util.function.IntPredicate;

/** Poikkeuksen hinta: pinojäljen keruu dominoi. */
final class Main {
    private static final int N = 200_000;
    private static final String[] SYOTTEET = {"123", "12x", "", "99999"};

    private Main() {
    }

    // @alku kevyt
    /** Kevyt poikkeus ilman pinojälkeä (writableStackTrace = false). */
    static final class Kelvoton extends RuntimeException {
        @Serial
        private static final long serialVersionUID = 1L;

        Kelvoton() {
            super("kelvoton", null, false, false);
        }
    }
    // @loppu kevyt

    // @alku tavat
    static boolean poikkeuksella(String s) {
        try {
            Integer.parseInt(s);
            return true;
        } catch (NumberFormatException e) {
            return false;
        }
    }

    static boolean tarkistamalla(String s) {
        if (s.isEmpty() || s.length() > 9) {
            return false;
        }
        for (int i = 0; i < s.length(); i++) {
            if (!Character.isDigit(s.charAt(i))) {
                return false;
            }
        }
        return true;
    }

    static boolean kevyella(String s) {
        try {
            if (!tarkistamalla(s)) {
                throw new Kelvoton();
            }
            return true;
        } catch (Kelvoton e) {
            return false;
        }
    }
    // @loppu tavat

    static long aika(IntPredicate tapa) {
        long paras = Long.MAX_VALUE;
        for (int kierros = 0; kierros < 15; kierros++) {
            long alku = System.nanoTime();
            int kelvollisia = 0;
            for (int i = 0; i < N; i++) {
                if (tapa.test(i)) {
                    kelvollisia++;
                }
            }
            paras = Math.min(paras, System.nanoTime() - alku);
            if (kelvollisia != N / 2) {
                throw new AssertionError(kelvollisia);
            }
        }
        return paras;
    }

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        long tPoikkeus = aika(i -> poikkeuksella(SYOTTEET[i % 4]));
        long tTarkistus = aika(i -> tarkistamalla(SYOTTEET[i % 4]));
        long tKevyt = aika(i -> kevyella(SYOTTEET[i % 4]));
        System.out.println("tarkistus vähintään 5 kertaa nopeampi: "
                + (tPoikkeus > 5 * tTarkistus));
        System.out.println("kevyt poikkeus vähintään 3 kertaa nopeampi: "
                + (tPoikkeus > 3 * tKevyt));
        System.err.printf("poikkeus %.1f ms, tarkistus %.1f ms, "
                + "kevyt %.1f ms%n", tPoikkeus / 1e6, tTarkistus / 1e6,
                tKevyt / 1e6);
    }
}
