/** Selittävä NullPointerException kertoo, mikä arvo oli null. */
final class Main {
    record Osoite(String katu, String postinumero) {
    }

    record Asiakas(String nimi, Osoite osoite) {
    }

    record Tilaus(int numero, Asiakas asiakas) {
    }

    private Main() {
    }

    public static void main(String[] args) {
        // @alku koodi
        var tilaus = new Tilaus(42, new Asiakas("Maija", null));
        String postinumero = tilaus.asiakas().osoite().postinumero();
        // @loppu koodi
        System.out.println(postinumero);
    }
}
