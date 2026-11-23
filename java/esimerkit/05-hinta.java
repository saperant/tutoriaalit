import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.util.ArrayList;
import java.util.List;
import java.util.function.LongSupplier;

/** Boksattujen lukujen hinta: List<Integer> vs. int[]. */
final class Main {
    private static final int N = 2_000_000;
    private static final int KIERROKSIA = 25;

    private Main() {
    }

    // @alku mittaus
    /** Paras aika nanosekunteina; alkukierrokset lämmittävät JIT:n. */
    static long parasAika(LongSupplier tehtava) {
        long paras = Long.MAX_VALUE;
        long tarkiste = 0;
        for (int i = 0; i < KIERROKSIA; i++) {
            long alku = System.nanoTime();
            tarkiste += tehtava.getAsLong();
            paras = Math.min(paras, System.nanoTime() - alku);
        }
        if (tarkiste == 42) { // estää tuloksen poistamisen
            System.out.println();
        }
        return paras;
    }
    // @loppu mittaus

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku vertailu
        int[] taulukko = new int[N];
        List<Integer> lista = new ArrayList<>(N);
        for (int i = 0; i < N; i++) {
            taulukko[i] = i % 1000;
            lista.add(i % 1000 + 1000); // yli välimuistin -128..127
        }
        long tTaulukko = parasAika(() -> {
            long s = 0;
            for (int x : taulukko) {
                s += x;
            }
            return s;
        });
        long tLista = parasAika(() -> {
            long s = 0;
            for (Integer x : lista) {
                s += x; // purku: x.intValue()
            }
            return s;
        });
        // @loppu vertailu
        System.out.printf("int[] vähintään 2 kertaa nopeampi: %b%n",
                tLista > 2 * tTaulukko);
        System.err.printf("int[] %.2f ms, List<Integer> %.2f ms%n",
                tTaulukko / 1e6, tLista / 1e6);
    }
}
