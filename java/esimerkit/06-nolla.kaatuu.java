import java.util.Map;

/** Automaattinen purku (unboxing) null-arvosta kaatuu. */
final class Main {
    private Main() {
    }

    public static void main(String[] args) {
        // @alku koodi
        Map<String, Integer> saldot = Map.of("ruuvi", 120, "mutteri", 80);
        int ruuveja = saldot.get("ruuvi");
        System.out.println("ruuveja " + ruuveja);
        int tulppia = saldot.get("tulppa"); // get palauttaa null
        System.out.println("tulppia " + tulppia);
        // @loppu koodi
    }
}
