import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.util.HashSet;
import java.util.Objects;
import java.util.Set;

/** Muuttuva avain rikkoo hajautustaulun. */
final class Main {
    private Main() {
    }

    // @alku luokka
    static final class Asiakas {
        private String sahkoposti;

        Asiakas(String sahkoposti) {
            this.sahkoposti = sahkoposti;
        }

        void vaihdaSahkoposti(String uusi) {
            this.sahkoposti = uusi;
        }

        @Override
        public boolean equals(Object o) {
            return o instanceof Asiakas a
                    && Objects.equals(sahkoposti, a.sahkoposti);
        }

        @Override
        public int hashCode() {
            return Objects.hashCode(sahkoposti);
        }
    }
    // @loppu luokka

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku kaytto
        Set<Asiakas> tilaajat = new HashSet<>();
        Asiakas maija = new Asiakas("maija@example.com");
        tilaajat.add(maija);
        maija.vaihdaSahkoposti("maija.v@example.com");

        System.out.println("contains: " + tilaajat.contains(maija));
        System.out.println("remove:   " + tilaajat.remove(maija));
        System.out.println("koko:     " + tilaajat.size());
        // Alkio on väärässä lokerossa: sitä ei löydä eikä saa poistettua.
        System.out.println("iteraattori löytää: "
                + tilaajat.stream().anyMatch(a -> a == maija));
        // @loppu kaytto
    }
}
