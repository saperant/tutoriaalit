import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.IOException;
import java.io.PrintStream;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.TreeMap;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.stream.Collectors;

/** Pikaoppaan koodi. */
final class Main {
    private Main() {
    }

    // @alku tyypit
    record Tuote(String nimi, long senttia) {
        Tuote {
            if (senttia < 0) {
                throw new IllegalArgumentException("hinta < 0");
            }
        }
    }

    sealed interface Tapahtuma permits Lisatty, Poistettu {
    }

    record Lisatty(Tuote tuote, int kpl) implements Tapahtuma {
    }

    record Poistettu(String nimi) implements Tapahtuma {
    }

    static String kuvaa(Tapahtuma t) {
        return switch (t) {
            case Lisatty(Tuote tuote, int kpl) when kpl > 1 ->
                    kpl + " x " + tuote.nimi();
            case Lisatty l -> l.tuote().nimi();
            case Poistettu(var nimi) -> "-" + nimi;
        };
    }
    // @loppu tyypit

    // @alku virheet
    static Optional<Tuote> hae(List<Tuote> tuotteet, String nimi) {
        return tuotteet.stream().filter(t -> t.nimi().equals(nimi))
                .findFirst();
    }

    static String lue(Path polku) {
        try {
            return Files.readString(polku, UTF_8);
        } catch (IOException e) {
            throw new UncheckedIOException("luku: " + polku, e);
        }
    }
    // @loppu virheet

    public static void main(String[] args)
            throws InterruptedException, ExecutionException {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku perus
        var tuotteet = new ArrayList<Tuote>();
        tuotteet.add(new Tuote("kahvi", 695));
        tuotteet.add(new Tuote("tee", 450));
        long summa = 0;
        for (Tuote t : tuotteet) {
            summa += t.senttia();
        }
        String teksti = """
                Tuotteita: %d
                Summa: %d snt""".formatted(tuotteet.size(), summa);
        System.out.println(teksti);
        // @loppu perus

        System.out.println(kuvaa(new Lisatty(tuotteet.get(0), 3)) + ", "
                + kuvaa(new Poistettu("tee")));

        // @alku kokoelmat
        List<String> nimet = tuotteet.stream()
                .sorted(Comparator.comparingLong(Tuote::senttia))
                .map(Tuote::nimi)
                .toList();                        // muuttumaton
        Map<Boolean, List<String>> kalliit = tuotteet.stream()
                .collect(Collectors.partitioningBy(t -> t.senttia() > 500,
                        Collectors.mapping(Tuote::nimi,
                                Collectors.toList())));
        Map<String, Integer> varasto = new TreeMap<>();
        varasto.merge("kahvi", 3, Integer::sum);
        varasto.merge("kahvi", 2, Integer::sum);
        System.out.println(nimet + " " + kalliit + " " + varasto);
        // @loppu kokoelmat

        System.out.println(hae(tuotteet, "mehu").map(Tuote::senttia)
                .orElse(0L));

        // @alku saikeet
        try (var suorittaja = Executors.newVirtualThreadPerTaskExecutor()) {
            Future<Long> f = suorittaja.submit(() -> 2L * 21);
            System.out.println(f.get());
        }
        // @loppu saikeet
    }
}
