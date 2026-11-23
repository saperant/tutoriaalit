import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.List;

/** Lukee varastorivit "tuote;määrä", raportoi virheelliset rivit. */
final class Main {
    record Rivi(String tuote, int maara) {
    }

    private Main() {
    }

    // @alku jasenna
    /** Jäsentää rivin tai heittää IllegalArgumentExceptionin. */
    static Rivi jasenna(String rivi) {
        String[] osat = rivi.split(";", -1);
        if (osat.length != 2) {
            throw new IllegalArgumentException(
                    "odotettiin 2 kenttää, saatiin " + osat.length);
        }
        String tuote = osat[0].strip();
        if (tuote.isEmpty()) {
            throw new IllegalArgumentException("tuote puuttuu");
        }
        int maara;
        try {
            maara = Integer.parseInt(osat[1].strip());
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException(
                    "määrä ei ole kokonaisluku: '" + osat[1] + "'", e);
        }
        if (maara < 0) {
            throw new IllegalArgumentException("negatiivinen määrä");
        }
        return new Rivi(tuote, maara);
    }
    // @loppu jasenna

    // @alku main
    public static void main(String[] args) throws IOException {
        // Tuloste UTF-8:na ympäristön merkistöstä riippumatta.
        System.setOut(new PrintStream(System.out, true, UTF_8));
        var lukija = new BufferedReader(
                new InputStreamReader(System.in, UTF_8));
        List<Rivi> rivit = new ArrayList<>();
        int numero = 0;
        String rivi;
        while ((rivi = lukija.readLine()) != null) {
            numero++;
            if (rivi.isBlank() || rivi.startsWith("#")) {
                continue;
            }
            try {
                rivit.add(jasenna(rivi));
            } catch (IllegalArgumentException e) {
                System.out.printf("rivi %d: %s%n", numero, e.getMessage());
            }
        }
        int yhteensa = rivit.stream().mapToInt(Rivi::maara).sum();
        System.out.println("""
                Kelvollisia rivejä: %d
                Tuotteita yhteensä: %d""".formatted(rivit.size(), yhteensa));
    }
    // @loppu main
}
