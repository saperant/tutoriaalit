import java.util.ArrayList;
import java.util.List;

/** Kokoelman muuttaminen for-each-silmukan aikana. */
final class Main {
    private Main() {
    }

    public static void main(String[] args) {
        // @alku koodi
        List<String> tilaukset = new ArrayList<>(
                List.of("A-1 peruttu", "A-2 avoin", "A-3 avoin"));
        for (String t : tilaukset) {
            if (t.endsWith("peruttu")) {
                tilaukset.remove(t); // muuttaa listaa iteroinnin aikana
            }
        }
        // @loppu koodi
        System.out.println(tilaukset);
    }
}
