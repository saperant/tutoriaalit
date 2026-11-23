import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

/** Muuttumattomat kokoelmat, näkymät ja kopiot. */
final class Main {
    private Main() {
    }

    static String kokeile(Runnable r) {
        try {
            r.run();
            return "ok";
        } catch (RuntimeException e) {
            return e.getClass().getSimpleName();
        }
    }

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku kaytto
        List<String> alkuperainen = new ArrayList<>(List.of("a", "b"));
        List<String> nakyma = Collections.unmodifiableList(alkuperainen);
        List<String> kopio = List.copyOf(alkuperainen);
        List<String> kiintea = Arrays.asList("x", "y");

        alkuperainen.add("c");
        System.out.println("näkymä: " + nakyma + ", kopio: " + kopio);
        System.out.println("nakyma.add:  " + kokeile(() -> nakyma.add("d")));
        System.out.println("kopio.add:   " + kokeile(() -> kopio.add("d")));
        System.out.println("asList.set:  "
                + kokeile(() -> kiintea.set(0, "z")));
        System.out.println("asList.add:  " + kokeile(() -> kiintea.add("z")));
        System.out.println("List.of(null): "
                + kokeile(() -> List.of("a", null)));
        // @loppu kaytto

        // @alku jarjestys
        List<Integer> luvut = new ArrayList<>(List.of(3, 1, 2));
        System.out.println(luvut.reversed() + " " + luvut.getFirst()
                + " " + luvut.getLast());
        // @loppu jarjestys
    }
}
