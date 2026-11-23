import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

/** Virtuaalisäikeet: tuhansia samanaikaisia odottavia tehtäviä. */
final class Main {
    private static final int TEHTAVIA = 10_000;

    private Main() {
    }

    // @alku haku
    /** Simuloi verkkokutsua: odottaa 50 ms ja palauttaa hinnan. */
    static int haeHinta(int tuote) throws InterruptedException {
        Thread.sleep(Duration.ofMillis(50));
        return tuote % 100;
    }
    // @loppu haku

    public static void main(String[] args)
            throws InterruptedException, ExecutionException {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku kaytto
        long alku = System.nanoTime();
        long summa = 0;
        try (var suorittaja = Executors.newVirtualThreadPerTaskExecutor()) {
            List<Future<Integer>> tulokset = new ArrayList<>();
            for (int i = 0; i < TEHTAVIA; i++) {
                int tuote = i;
                tulokset.add(suorittaja.submit(() -> haeHinta(tuote)));
            }
            for (Future<Integer> f : tulokset) {
                summa += f.get();
            }
        } // close() odottaa, että kaikki tehtävät ovat valmiita
        Duration kesto = Duration.ofNanos(System.nanoTime() - alku);
        System.out.println("summa: " + summa);
        System.out.println("alle 5 s (peräkkäin 500 s): "
                + (kesto.toSeconds() < 5));
        // @loppu kaytto
    }
}
