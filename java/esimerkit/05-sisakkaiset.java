import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Iterator;
import java.util.List;
import java.util.NoSuchElementException;

// @alku sarja
/** Viimeisimmät mittaukset: kun sarja on täynnä, vanhin putoaa pois. */
final class Mittaussarja implements Iterable<Integer> {
    private final int[] arvot;
    private int alku;               // vanhimman arvon indeksi
    private int maara;

    Mittaussarja(int koko) {
        arvot = new int[koko];
    }

    void lisaa(int arvo) {
        arvot[(alku + maara) % arvot.length] = arvo;
        if (maara < arvot.length) {
            maara++;
        } else {
            alku = (alku + 1) % arvot.length;
        }
    }

    /** Staattinen sisäkkäinen luokka: ei viitettä ulompaan olioon. */
    static final class Rajat {
        private final int pienin;
        private final int suurin;

        private Rajat(int pienin, int suurin) {
            this.pienin = pienin;
            this.suurin = suurin;
        }

        @Override
        public String toString() {
            return pienin + "…" + suurin;
        }
    }

    Rajat rajat() {
        int pienin = Integer.MAX_VALUE;
        int suurin = Integer.MIN_VALUE;
        for (int arvo : this) {
            pienin = Math.min(pienin, arvo);
            suurin = Math.max(suurin, arvo);
        }
        return new Rajat(pienin, suurin);
    }

    /** Sisäluokka: näkee ulomman olion kentät arvot, alku ja maara. */
    private final class Kulkija implements Iterator<Integer> {
        private int luettu;

        @Override
        public boolean hasNext() {
            return luettu < maara;
        }

        @Override
        public Integer next() {
            if (!hasNext()) {
                throw new NoSuchElementException();
            }
            return arvot[(alku + luettu++) % arvot.length];
        }
    }

    /** Iterable-rajapinnan metodi: tekee tyypistä for-each-kelpoisen. */
    @Override
    public Iterator<Integer> iterator() {
        return new Kulkija();
    }
}
// @loppu sarja

/** Sisäkkäiset luokat, sisäluokat ja nimettömät luokat. */
final class Main {
    private Main() {
    }

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku kaytto
        var sarja = new Mittaussarja(4);
        for (int arvo : new int[] {21, 23, 22, 25, 24, 20}) {
            sarja.lisaa(arvo);
        }
        for (int arvo : sarja) {
            System.out.print(arvo + " ");
        }
        Mittaussarja.Rajat rajat = sarja.rajat();
        System.out.println("rajat " + rajat);
        // @loppu kaytto

        // @alku nimeton
        Comparator<String> pituus = new Comparator<>() {
            @Override
            public int compare(String a, String b) {
                return Integer.compare(a.length(), b.length());
            }
        };
        Comparator<String> sama =
                (a, b) -> Integer.compare(a.length(), b.length());

        List<String> nimet =
                new ArrayList<>(List.of("lämpötila", "paine", "kosteus"));
        nimet.sort(pituus);
        System.out.println(nimet);
        nimet.sort(sama.reversed());
        System.out.println(nimet);
        // @loppu nimeton
    }
}
