import java.util.Locale;

/** Kääntäjä tarkistaa, että switch kattaa suljetun tyypin alatyypit. */
final class Main {
    private Main() {
    }

    // @alku koodi
    sealed interface Muoto {
    }

    record Ympyra(double r) implements Muoto {
    }

    record Suorakulmio(double a, double b) implements Muoto {
    }

    record Kolmio(double kanta, double korkeus) implements Muoto { // @virhe
    } // @virhe

    static double ala(Muoto m) {
        return switch (m) {
            case Ympyra y -> Math.PI * y.r() * y.r();
            case Suorakulmio s -> s.a() * s.b();
        };
    }
    // @loppu koodi

    public static void main(String[] args) {
        System.out.printf(Locale.ROOT, "%.2f%n",
                ala(new Suorakulmio(2, 3)));
    }
}
