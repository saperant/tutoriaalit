import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

/** CompletableFuture-ketjut ja ConcurrentHashMapin atomiset operaatiot. */
final class Main {
    private Main() {
    }

    // @alku palvelut
    static int hinta(String tuote) {
        return switch (tuote) {
            case "kahvi" -> 695;
            case "tee" -> 450;
            default -> throw new IllegalArgumentException("tuntematon: "
                    + tuote);
        };
    }

    static int varastossa(String tuote) {
        return tuote.length() * 10;
    }
    // @loppu palvelut

    public static void main(String[] args) throws InterruptedException {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        ExecutorService allas = Executors.newVirtualThreadPerTaskExecutor();
        // @alku ketju
        for (String tuote : new String[] {"kahvi", "mehu"}) {
            var h = CompletableFuture.supplyAsync(() -> hinta(tuote), allas);
            var v = CompletableFuture.supplyAsync(() -> varastossa(tuote),
                    allas);
            String rivi = h.thenCombine(v, (hinta, kpl) ->
                            tuote + ": " + hinta + " snt, " + kpl + " kpl")
                    .orTimeout(1, TimeUnit.SECONDS)
                    .exceptionally(e -> tuote + ": virhe ("
                            + e.getCause().getMessage() + ")")
                    .join();
            System.out.println(rivi);
        }
        // @loppu ketju

        // @alku muisti
        var laskettu = new AtomicInteger();
        var valimuisti = new ConcurrentHashMap<String, Integer>();
        var tehtavat = new CompletableFuture<?>[100];
        for (int i = 0; i < tehtavat.length; i++) {
            String tuote = i % 2 == 0 ? "kahvi" : "tee";
            tehtavat[i] = CompletableFuture.runAsync(() ->
                    valimuisti.computeIfAbsent(tuote, t -> {
                        laskettu.incrementAndGet();
                        return hinta(t);
                    }), allas);
        }
        CompletableFuture.allOf(tehtavat).join();
        System.out.println(valimuisti.size() + " avainta, laskettu "
                + laskettu.get() + " kertaa");
        // @loppu muisti
        allas.shutdown();
        if (!allas.awaitTermination(5, TimeUnit.SECONDS)) {
            throw new IllegalStateException("tehtävät eivät päättyneet");
        }
    }
}
