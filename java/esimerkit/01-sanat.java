import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

/** Laskee syötteen yleisimmät sanat. */
final class Main {
    private static final int NAYTETTAVIA = 5;

    private Main() {
    }

    public static void main(String[] args) throws IOException {
        // Tuloste UTF-8:na ympäristön merkistöstä riippumatta.
        System.setOut(new PrintStream(System.out, true, UTF_8));
        var lukija = new BufferedReader(
                new InputStreamReader(System.in, UTF_8));
        Map<String, Integer> maarat = new HashMap<>();
        String rivi;
        while ((rivi = lukija.readLine()) != null) {
            for (String sana : rivi.toLowerCase(Locale.ROOT)
                    .split("[^\\p{L}]+")) {
                if (!sana.isEmpty()) {
                    maarat.merge(sana, 1, Integer::sum);
                }
            }
        }
        maarat.entrySet().stream()
                .sorted(Map.Entry.<String, Integer>comparingByValue()
                        .reversed()
                        .thenComparing(Map.Entry.comparingByKey()))
                .limit(NAYTETTAVIA)
                .forEach(e -> System.out.printf("%3d %s%n",
                        e.getValue(), e.getKey()));
    }
}
