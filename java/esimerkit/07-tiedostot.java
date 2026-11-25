import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.BufferedWriter;
import java.io.IOException;
import java.io.PrintStream;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.List;
import java.util.stream.Stream;

/** Tiedostot: Path ja Files. */
final class Main {
    private Main() {
    }

    public static void main(String[] args) throws IOException {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        Path juuri = Files.createTempDirectory("tiedostot");

        // @alku polku
        Path loki = juuri.resolve("lokit").resolve("palvelu.log");
        System.out.println(loki.getFileName() + " "
                + juuri.relativize(loki) + " "
                + Path.of("lokit/../asetukset.conf").normalize());
        // @loppu polku

        // @alku kirjoitus
        Files.createDirectories(loki.getParent());
        Files.writeString(loki, "08:00 INFO käynnistys\n", UTF_8);
        try (BufferedWriter ulos = Files.newBufferedWriter(loki, UTF_8,
                StandardOpenOption.APPEND)) {
            ulos.write("08:01 WARN levytila 91 %\n");
            ulos.write("08:02 ERROR yhteys katkesi\n");
            ulos.write("08:03 INFO yhteys palasi\n");
        }
        // @loppu kirjoitus

        // @alku luku
        List<String> rivit = Files.readAllLines(loki, UTF_8);
        System.out.println(rivit.size() + " riviä, " + Files.size(loki)
                + " tavua");
        try (Stream<String> virta = Files.lines(loki, UTF_8)) {
            virta.filter(r -> !r.contains(" INFO "))
                    .forEach(System.out::println);
        }
        // @loppu luku

        // @alku hakemisto
        Files.copy(loki, juuri.resolve("varmuuskopio.log"));
        try (Stream<Path> polut = Files.walk(juuri)) {
            polut.filter(Files::isRegularFile)
                    .map(p -> juuri.relativize(p).toString())
                    .sorted()
                    .forEach(System.out::println);
        }
        try {
            Files.readString(juuri.resolve("puuttuu.txt"), UTF_8);
        } catch (NoSuchFileException e) {
            System.out.println("ei löydy: "
                    + juuri.relativize(Path.of(e.getFile())));
        }
        // @loppu hakemisto

        // Siivous: lapset ennen vanhempia.
        try (Stream<Path> polut = Files.walk(juuri)) {
            for (Path p : polut.sorted((a, b) -> b.compareTo(a)).toList()) {
                Files.delete(p);
            }
        }
        System.out.println("siivottu: " + Files.notExists(juuri));
    }
}
