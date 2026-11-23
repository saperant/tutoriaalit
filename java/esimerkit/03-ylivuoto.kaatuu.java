/** Kokonaisluvun ylivuoto: hiljainen kierto ja tarkistettu laskenta. */
final class Main {
    private Main() {
    }

    public static void main(String[] args) {
        int tiedostoja = 50_000;
        int koko = 65_536;
        // Ylivuoto kiertää hiljaa negatiiviseksi.
        System.out.println("int:  " + tiedostoja * koko);
        // Oikea tulos, kun laskenta tehdään long-tyypillä.
        System.out.println("long: " + (long) tiedostoja * koko);
        // Math.*Exact heittää poikkeuksen ylivuodosta.
        System.out.println(Math.multiplyExact(tiedostoja, koko));
    }
}
