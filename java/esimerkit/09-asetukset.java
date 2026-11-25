import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.IOException;
import java.io.PrintStream;
import java.io.Serial;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Poikkeusten kerrokset: kääriminen syyn kanssa ja ketjun tulostus. */
final class Main {
    private Main() {
    }

    // @alku virhe
    /** Tarkistettu poikkeus: kutsujan on päätettävä, mitä tehdään. */
    static final class AsetusVirhe extends Exception {
        @Serial
        private static final long serialVersionUID = 1L;

        AsetusVirhe(String viesti, Throwable syy) {
            super(viesti, syy);
        }
    }
    // @loppu virhe

    // @alku jasennys
    static Map<String, Integer> jasenna(List<String> rivit) {
        Map<String, Integer> tulos = new HashMap<>();
        for (int i = 0; i < rivit.size(); i++) {
            String[] osat = rivit.get(i).split("=", 2);
            try {
                tulos.put(osat[0].strip(), Integer.parseInt(osat[1].strip()));
            } catch (NumberFormatException
                    | ArrayIndexOutOfBoundsException e) {
                throw new IllegalArgumentException("rivi " + (i + 1)
                        + ": odotettiin avain=luku", e);
            }
        }
        return tulos;
    }

    static Map<String, Integer> lataa(Path polku) throws AsetusVirhe {
        try {
            return jasenna(Files.readAllLines(polku, UTF_8));
        } catch (IOException | IllegalArgumentException e) {
            throw new AsetusVirhe("asetusten lataus: " + polku, e);
        }
    }
    // @loppu jasennys

    // @alku ketju
    static void tulostaKetju(Throwable t) {
        String sisennys = "";
        for (Throwable s = t; s != null; s = s.getCause()) {
            System.out.println(sisennys + s.getClass().getSimpleName()
                    + ": " + s.getMessage());
            sisennys += "  ";
        }
    }
    // @loppu ketju

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku kaytto
        try {
            Files.writeString(Path.of("ok.conf"), "portti = 8080\n");
            Files.writeString(Path.of("rikki.conf"), "portti = 80a\n");
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
        for (String nimi : List.of("ok.conf", "rikki.conf", "puuttuu.conf")) {
            try {
                System.out.println(nimi + ": " + lataa(Path.of(nimi)));
            } catch (AsetusVirhe e) {
                tulostaKetju(e);
                if (e.getCause() instanceof NoSuchFileException) {
                    System.out.println("  -> käytetään oletuksia");
                }
            }
        }
        // @loppu kaytto
    }
}
