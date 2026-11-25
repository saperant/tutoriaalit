import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.util.Arrays;

/** Taulukot: luonti, indeksointi, viitteet ja moniulotteisuus. */
final class Main {
    private Main() {
    }

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku perus
        int[] lampotilat = {-3, 1, 4, 2, -5, 0, 3};  // alkiot luettelona
        double[] keskiarvot = new double[3];         // oletusarvo 0.0
        String[] paivat = new String[2];             // oletusarvo null

        long summa = 0;
        for (int lampotila : lampotilat) {
            summa += lampotila;
        }
        System.out.println(lampotilat.length + " mittausta, summa " + summa
                + ", viimeinen " + lampotilat[lampotilat.length - 1]);
        System.out.println(Arrays.toString(keskiarvot) + " "
                + Arrays.toString(paivat));
        try {
            lampotilat[7] = 1;
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("virhe: " + e.getMessage());
        }
        // @loppu perus

        // @alku viite
        int[] sama = lampotilat;                     // sama taulukko
        int[] kopio = Arrays.copyOf(lampotilat, lampotilat.length);
        sama[0] = 99;
        System.out.println(lampotilat[0] + " " + kopio[0]);
        kopio[0] = 99;
        System.out.println(lampotilat.equals(kopio) + " "
                + Arrays.equals(lampotilat, kopio));
        // @loppu viite

        // @alku moni
        int[][] ruudukko = new int[2][3];            // 2 riviä, 3 saraketta
        ruudukko[1][2] = 7;
        int[][] kolmio = {{1}, {1, 1}, {1, 2, 1}};   // rivit eripituisia
        System.out.println(Arrays.deepToString(ruudukko) + " "
                + kolmio[2].length);
        // @loppu moni
    }
}
