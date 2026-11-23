import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;
import java.util.Locale;

/** Laskun summat: double ei sovellu rahalle, BigDecimal soveltuu. */
final class Main {
    // @alku rivi
    record Rivi(String tuote, int maara, BigDecimal yksikkohinta) {
        BigDecimal summa() {
            return yksikkohinta.multiply(BigDecimal.valueOf(maara));
        }
    }
    // @loppu rivi

    private static final BigDecimal ALV = new BigDecimal("0.255");

    private Main() {
    }

    public static void main(String[] args) {
        // @alku utf
        // Tuloste UTF-8:na ympäristön merkistöstä riippumatta.
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @loppu utf
        // @alku double
        double d = 0.1 + 0.2;
        System.out.println("0.1 + 0.2 = " + d);
        System.out.println("yhtä suuri kuin 0.3: " + (d == 0.3));
        // @loppu double

        // @alku lasku
        List<Rivi> rivit = List.of(
                new Rivi("Kahvi 500 g", 3, new BigDecimal("6.95")),
                new Rivi("Suodatinpussit", 2, new BigDecimal("2.49")));
        BigDecimal veroton = BigDecimal.ZERO;
        for (Rivi r : rivit) {
            veroton = veroton.add(r.summa());
            System.out.printf(Locale.ROOT, "%-16s %3d x %6.2f = %7.2f%n",
                    r.tuote(), r.maara(), r.yksikkohinta(), r.summa());
        }
        BigDecimal vero = veroton.multiply(ALV)
                .setScale(2, RoundingMode.HALF_UP);
        System.out.printf(Locale.ROOT, "Veroton %21.2f%n", veroton);
        System.out.printf(Locale.ROOT, "ALV 25,5 %% %18.2f%n", vero);
        System.out.printf(Locale.ROOT, "Yhteensä %20.2f%n",
                veroton.add(vero));
        // @loppu lasku

        // @alku muotoilu
        var summa = new BigDecimal("1234.5");
        System.out.println(String.format(Locale.ROOT, "%.2f", summa));
        System.out.println(String.format(Locale.forLanguageTag("fi-FI"),
                "%.2f", summa));
        System.out.println(new BigDecimal("2.50")
                .equals(new BigDecimal("2.5")));
        System.out.println(new BigDecimal("2.50")
                .compareTo(new BigDecimal("2.5")) == 0);
        // @loppu muotoilu
    }
}
