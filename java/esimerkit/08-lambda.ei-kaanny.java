import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

/** Tarkistettu poikkeus ei mahdu Function- tai Consumer-lambdaan. */
final class Main {
    private Main() {
    }

    // @alku apu
    static void poista(Path polku) {
        try {
            Files.deleteIfExists(polku);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
    // @loppu apu

    public static void main(String[] args) throws IOException {
        List<Path> polut = List.of(Path.of("a.tmp"), Path.of("b.tmp"));
        for (Path p : polut) {
            Files.writeString(p, "x");
        }
        // @alku koodi
        polut.forEach(p -> Files.delete(p)); // @virhe: IOException
        polut.forEach(Main::poista);
        // @loppu koodi
        System.out.println(polut.stream().noneMatch(Files::exists));
    }
}
