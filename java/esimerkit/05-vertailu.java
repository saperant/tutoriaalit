import java.util.Objects;

/** Viitevertailu (==) ja arvovertailu (equals). */
final class Main {
    private Main() {
    }

    // @alku luokka
    /** Arvoluokka: equals ja hashCode samoista kentistä. */
    static final class Tuotekoodi {
        private final String koodi;

        Tuotekoodi(String koodi) {
            this.koodi = Objects.requireNonNull(koodi);
        }

        @Override
        public boolean equals(Object o) {
            return o instanceof Tuotekoodi t && koodi.equals(t.koodi);
        }

        @Override
        public int hashCode() {
            return koodi.hashCode();
        }
    }

    record Koodi(String koodi) {
    }
    // @loppu luokka

    public static void main(String[] args) {
        // @alku vertailu
        String a = "kahvi";
        String b = new StringBuilder("kah").append("vi").toString();
        System.out.println("a == b:      " + (a == b));
        System.out.println("a.equals(b): " + a.equals(b));

        Integer pieni1 = 127;
        Integer pieni2 = 127;
        Integer suuri1 = 128;
        Integer suuri2 = 128;
        System.out.println("127 == 127:  " + (pieni1 == pieni2));
        System.out.println("128 == 128:  " + (suuri1 == suuri2));
        System.out.println("128 equals:  " + suuri1.equals(suuri2));

        System.out.println("luokka:      "
                + new Tuotekoodi("A-1").equals(new Tuotekoodi("A-1")));
        System.out.println("record:      "
                + new Koodi("A-1").equals(new Koodi("A-1")));
        // @loppu vertailu
    }
}
