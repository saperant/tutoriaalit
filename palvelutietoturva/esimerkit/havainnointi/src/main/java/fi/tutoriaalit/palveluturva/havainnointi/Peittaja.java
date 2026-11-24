package fi.tutoriaalit.palveluturva.havainnointi;

import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;
import java.util.regex.Pattern;

/**
 * Poistaa salaisuudet ja henkilötiedot ennen kuin ne päätyvät lokiin.
 * Loki on usein laajemmin luettavissa kuin tietokanta, ja sieltä
 * vuotanut token on yhtä käyttökelpoinen kuin mikä tahansa muu.
 */
public final class Peittaja {

    // @alku peita
    private static final Pattern SALAINEN_AVAIN = Pattern.compile(
            "(?i).*(salasana|password|token|secret|avain|authorization)"
            + ".*");
    private static final Pattern KORTTI =
            Pattern.compile("\\b\\d{12,15}(\\d{4})\\b");
    private static final Pattern BEARER =
            Pattern.compile("(?i)bearer\\s+[A-Za-z0-9._~+/=-]+");

    public static Map<String, String> peita(Map<String, String> tiedot) {
        Map<String, String> tulos = new TreeMap<>();
        tiedot.forEach((avain, arvo) -> tulos.put(avain,
                SALAINEN_AVAIN.matcher(avain.toLowerCase(Locale.ROOT))
                        .matches() ? "[peitetty]" : peitaArvo(arvo)));
        return tulos;
    }

    static String peitaArvo(String arvo) {
        String s = BEARER.matcher(arvo).replaceAll("Bearer [peitetty]");
        return KORTTI.matcher(s).replaceAll("****$1");
    }
    // @loppu peita

    private Peittaja() {}
}
