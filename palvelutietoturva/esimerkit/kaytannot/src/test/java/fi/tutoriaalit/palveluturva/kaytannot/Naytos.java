package fi.tutoriaalit.palveluturva.kaytannot;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/**
 * Näytösajon tuloste: rivit kootaan tauluksi, kirjoitetaan hakemistoon
 * target/naytos ja verrataan tallennettuun tiedostoon
 * esimerkit/naytos/NIMI.odotettu. Kirjan tulostelohkot ovat näitä
 * tiedostoja, joten ne ovat aina oikean ajon tuloksia.
 */
public final class Naytos {

    private final String nimi;
    private final List<String> rivit = new ArrayList<>();

    public Naytos(String nimi) {
        this.nimi = nimi;
    }

    /** Lisää rivin sellaisenaan. */
    public Naytos rivi(String rivi) {
        rivit.add(rivi);
        return this;
    }

    /** Lisää taulun: sarakkeet tasataan leveimmän solun mukaan. */
    public Naytos taulu(List<List<String>> taulu) {
        int[] leveys = new int[taulu.get(0).size()];
        for (List<String> r : taulu) {
            for (int i = 0; i < r.size(); i++) {
                leveys[i] = Math.max(leveys[i], r.get(i).length());
            }
        }
        for (List<String> r : taulu) {
            var sb = new StringBuilder();
            for (int i = 0; i < r.size(); i++) {
                sb.append(String.format("%-" + (leveys[i] + 2) + "s",
                        r.get(i)));
            }
            rivit.add(sb.toString().stripTrailing());
        }
        return this;
    }

    /** Kirjoittaa tulosteen ja vertaa sen tallennettuun. */
    public void vertaa() throws IOException {
        String tuloste = String.join("\n", rivit) + "\n";
        Path ulos = Path.of("target", "naytos", nimi + ".txt");
        Files.createDirectories(ulos.getParent());
        Files.writeString(ulos, tuloste);
        Path odotettu = Path.of("..", "naytos", nimi + ".odotettu");
        assertThat(odotettu).as("aja make paivita-naytokset").exists();
        assertThat(tuloste).isEqualTo(Files.readString(odotettu));
    }
}
