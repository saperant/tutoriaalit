/** switch-lauseke tarkistaa, että kaikki enum-arvot käsitellään. */
final class Main {
    // @alku koodi
    enum Koko {
        PIENI,
        SUURI,
        JATTI, // @virhe: uusi arvo, jota switch ei käsittele
    }

    static int postimaksuSentteina(Koko koko) {
        return switch (koko) {
            case PIENI -> 590;
            case SUURI -> 1290;
        };
    }
    // @loppu koodi

    private Main() {
    }

    public static void main(String[] args) {
        System.out.println(postimaksuSentteina(Koko.SUURI));
    }
}
