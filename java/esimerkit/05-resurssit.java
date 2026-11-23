/** try-with-resources: sulkemisjärjestys ja tukahdutetut poikkeukset. */
final class Main {
    private Main() {
    }

    // @alku resurssi
    /** Resurssi, joka tulostaa avaamisen ja sulkemisen. */
    static final class Yhteys implements AutoCloseable {
        private final String nimi;
        private final boolean sulkeminenEpaonnistuu;

        Yhteys(String nimi, boolean sulkeminenEpaonnistuu) {
            this.nimi = nimi;
            this.sulkeminenEpaonnistuu = sulkeminenEpaonnistuu;
            System.out.println("avataan " + nimi);
        }

        void laheta(String viesti) {
            if (viesti.isEmpty()) {
                throw new IllegalArgumentException("tyhja viesti");
            }
            System.out.println(nimi + " <- " + viesti);
        }

        @Override
        public void close() {
            System.out.println("suljetaan " + nimi);
            if (sulkeminenEpaonnistuu) {
                throw new IllegalStateException(nimi + ": sulkeminen");
            }
        }
    }
    // @loppu resurssi

    public static void main(String[] args) {
        // @alku kaytto
        try (var tietokanta = new Yhteys("tietokanta", false);
                var jono = new Yhteys("jono", true)) {
            tietokanta.laheta("tilaus 42");
            jono.laheta("");
        } catch (IllegalArgumentException e) {
            System.out.println("virhe: " + e.getMessage());
            for (Throwable t : e.getSuppressed()) {
                System.out.println("  tukahdutettu: " + t.getMessage());
            }
        }
        // @loppu kaytto
    }
}
