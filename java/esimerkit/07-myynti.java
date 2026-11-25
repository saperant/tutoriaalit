import static java.nio.charset.StandardCharsets.UTF_8;
import static java.util.stream.Collectors.counting;
import static java.util.stream.Collectors.groupingBy;
import static java.util.stream.Collectors.mapping;
import static java.util.stream.Collectors.partitioningBy;
import static java.util.stream.Collectors.summingLong;
import static java.util.stream.Collectors.toCollection;
import static java.util.stream.Collectors.toMap;

import java.io.PrintStream;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

/** Myyntiraportti kokoelmilla ja streameilla. */
final class Main {
    record Myynti(String myymala, String tuote, int kpl, long senttia) {
    }

    static final List<Myynti> MYYNNIT = List.of(
            new Myynti("Tampere", "kahvi", 3, 2085),
            new Myynti("Turku", "tee", 1, 450),
            new Myynti("Tampere", "tee", 2, 900),
            new Myynti("Oulu", "kahvi", 5, 3475),
            new Myynti("Turku", "kahvi", 1, 695),
            new Myynti("Oulu", "kaakao", 2, 1180));

    private Main() {
    }

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku ryhmittely
        Map<String, Long> myymaloittain = MYYNNIT.stream()
                .collect(groupingBy(Myynti::myymala, TreeMap::new,
                        summingLong(Myynti::senttia)));
        System.out.println("Myymälöittäin: " + myymaloittain);

        Map<String, Long> tuotteittain = MYYNNIT.stream()
                .collect(groupingBy(Myynti::tuote, TreeMap::new, counting()));
        System.out.println("Tapahtumia:    " + tuotteittain);

        Map<Boolean, Set<String>> isot = MYYNNIT.stream()
                .collect(partitioningBy(m -> m.senttia() >= 1000,
                        mapping(Myynti::myymala,
                                toCollection(TreeSet::new))));
        System.out.println("Vähintään 10 €: " + isot.get(true));
        // @loppu ryhmittely

        // @alku paras
        Myynti suurin = MYYNNIT.stream()
                .max(Comparator.comparingLong(Myynti::senttia))
                .orElseThrow();
        System.out.println("Suurin:        " + suurin);
        // @loppu paras

        // @alku tomap
        Map<String, Integer> kpl = MYYNNIT.stream()
                .collect(toMap(Myynti::tuote, Myynti::kpl, Integer::sum,
                        TreeMap::new));
        System.out.println("Kappaleet:     " + kpl);
        // @loppu tomap

        // @alku silmukka
        Map<String, Integer> kpl2 = new TreeMap<>();
        for (Myynti m : MYYNNIT) {
            kpl2.merge(m.tuote(), m.kpl(), Integer::sum);
        }
        System.out.println("Silmukalla:    " + kpl2);
        // @loppu silmukka
    }
}
