import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.util.Arrays;
import java.util.List;

/** Taulukot kirjastossa: Arrays, muunnokset ja kovarianssi. */
final class Main {
    private Main() {
    }

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku arrays
        int[] pisteet = {72, 95, 58, 81};
        Arrays.sort(pisteet);
        System.out.println(Arrays.toString(pisteet) + ", 81 on indeksissä "
                + Arrays.binarySearch(pisteet, 81));
        int[] parhaat = Arrays.copyOfRange(pisteet, 2, 4);
        System.out.println(Arrays.toString(parhaat) + ", keskiarvo "
                + Arrays.stream(pisteet).average().orElseThrow());
        // @loppu arrays

        // @alku muunnos
        String[] nimet = {"Liisa", "Aino", "Matti"};
        List<String> nakyma = Arrays.asList(nimet);  // näkymä taulukkoon
        List<String> kopio = List.of(nimet);         // muuttumaton kopio
        nimet[0] = "Sari";
        System.out.println(nakyma.get(0) + " " + kopio.get(0));
        String[] takaisin = kopio.toArray(String[]::new);
        System.out.println(takaisin.length);
        // @loppu muunnos

        // @alku kovarianssi
        Object[] oliot = nimet;                      // kääntyy
        try {
            oliot[0] = 42;                           // kaatuu ajossa
        } catch (ArrayStoreException e) {
            System.out.println("ArrayStoreException: " + e.getMessage());
        }
        // @loppu kovarianssi
    }
}
