import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Objects;

/** Arvotyyppi recordina: validointi, tehdasmetodit ja muuttumattomuus. */
final class Main {
    private Main() {
    }

    // @alku raha
    /** Rahasumma sentteinä. Muuttumaton; aritmetiikka palauttaa uuden. */
    record Raha(long senttia) implements Comparable<Raha> {
        static final Raha NOLLA = new Raha(0);

        Raha { // kompakti konstruktori: validointi ennen kenttien asetusta
            if (senttia < 0) {
                throw new IllegalArgumentException("negatiivinen summa");
            }
        }

        /** Jäsentää muodon "12.50" tai "12,50". */
        static Raha euroa(String teksti) {
            Objects.requireNonNull(teksti, "teksti");
            BigDecimal arvo;
            try {
                arvo = new BigDecimal(teksti.strip().replace(',', '.'));
            } catch (NumberFormatException e) {
                throw new IllegalArgumentException("ei summa: " + teksti, e);
            }
            try {
                return new Raha(arvo.movePointRight(2)
                        .setScale(0, RoundingMode.UNNECESSARY)
                        .longValueExact());
            } catch (ArithmeticException e) {
                throw new IllegalArgumentException(
                        "liikaa desimaaleja: " + teksti, e);
            }
        }

        Raha plus(Raha muu) {
            return new Raha(Math.addExact(senttia, muu.senttia));
        }

        Raha kertaa(int maara) {
            return new Raha(Math.multiplyExact(senttia, maara));
        }

        @Override
        public int compareTo(Raha muu) {
            return Long.compare(senttia, muu.senttia);
        }

        @Override
        public String toString() {
            return String.format("%d,%02d €", senttia / 100, senttia % 100);
        }
    }
    // @loppu raha

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku kaytto
        Raha kahvi = Raha.euroa("6,95");
        Raha yhteensa = Raha.NOLLA.plus(kahvi.kertaa(3))
                .plus(Raha.euroa("2.49"));
        System.out.println(yhteensa);
        System.out.println(kahvi.equals(Raha.euroa("6.950")));
        for (String syote : new String[] {"-1", "1.005", "abc"}) {
            try {
                Raha.euroa(syote);
            } catch (IllegalArgumentException e) {
                System.out.println(syote + ": " + e.getMessage());
            }
        }
        // @loppu kaytto
    }
}
