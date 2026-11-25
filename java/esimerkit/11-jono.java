import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

/** Tuottaja ja kuluttajat rajatulla jonolla ja lopetusmerkillä. */
final class Main {
    private static final int KULUTTAJIA = 3;

    // @alku tyypit
    sealed interface Viesti {
    }

    record Tyo(int numero) implements Viesti {
    }

    record Lopeta() implements Viesti {
    }
    // @loppu tyypit

    private Main() {
    }

    // @alku kuluttaja
    static long kuluta(BlockingQueue<Viesti> jono)
            throws InterruptedException {
        long summa = 0;
        while (true) {
            switch (jono.take()) {
                case Tyo(int n) -> summa += (long) n * n;
                case Lopeta l -> {
                    return summa;
                }
            }
        }
    }
    // @loppu kuluttaja

    public static void main(String[] args)
            throws InterruptedException, ExecutionException {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku kaytto
        BlockingQueue<Viesti> jono = new ArrayBlockingQueue<>(16);
        ExecutorService allas = Executors.newFixedThreadPool(KULUTTAJIA);
        try {
            List<Future<Long>> tulokset = new ArrayList<>();
            for (int i = 0; i < KULUTTAJIA; i++) {
                tulokset.add(allas.submit(() -> kuluta(jono)));
            }
            for (int n = 1; n <= 1000; n++) {
                jono.put(new Tyo(n)); // odottaa, jos jono on täynnä
            }
            for (int i = 0; i < KULUTTAJIA; i++) {
                jono.put(new Lopeta());
            }
            long summa = 0;
            for (Future<Long> f : tulokset) {
                summa += f.get();
            }
            System.out.println("neliöiden summa: " + summa);
        } finally {
            allas.shutdown();
        }
        // @loppu kaytto
    }
}
