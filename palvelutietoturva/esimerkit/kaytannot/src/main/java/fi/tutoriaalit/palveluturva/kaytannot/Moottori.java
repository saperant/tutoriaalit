package fi.tutoriaalit.palveluturva.kaytannot;

import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Käytäntöjen arviointi (päätöspiste, PDP). Säännöt samassa
 * järjestyksessä kuin pilvien IAM:ssä:
 * 1. nimenomainen esto voittaa aina,
 * 2. muuten pyyntö sallitaan, jos jokin lauseke sallii sen,
 * 3. muuten pyyntö estetään (oletuksena esto).
 */
public final class Moottori {

    // @alku pyynto
    /** Kuka tekee mitä millekin, ja missä tilanteessa. */
    public record Pyynto(String toimija, String toiminto, String resurssi,
                         Map<String, String> konteksti) {}

    public record Paatos(boolean sallittu, String peruste) {}
    // @loppu pyynto

    private final List<Kaytanto> kaytannot;

    public Moottori(List<Kaytanto> kaytannot) {
        this.kaytannot = List.copyOf(kaytannot);
    }

    // @alku arvioi
    public Paatos arvioi(Pyynto p) {
        String salliva = null;
        for (Kaytanto k : kaytannot) {
            for (Kaytanto.Lauseke l : k.lausekkeet()) {
                if (!osuu(l, p)) {
                    continue;
                }
                if (l.vaikutus() == Kaytanto.Vaikutus.ESTA) {
                    return new Paatos(false, "esto: " + k.nimi() + "/"
                            + l.tunnus());
                }
                if (salliva == null) {
                    salliva = k.nimi() + "/" + l.tunnus();
                }
            }
        }
        return salliva != null ? new Paatos(true, "sallittu: " + salliva)
                : new Paatos(false, "oletuksena estetty");
    }

    static boolean osuu(Kaytanto.Lauseke l, Pyynto p) {
        return kohdistuu(l, p) && l.ehdot().entrySet().stream()
                .allMatch(e -> e.getValue().equals(
                        p.konteksti().get(e.getKey())));
    }

    /** Osuvatko toiminto ja resurssi (ehdoista välittämättä)? */
    static boolean kohdistuu(Kaytanto.Lauseke l, Pyynto p) {
        return l.toiminnot().stream().anyMatch(t -> vastaa(t, p.toiminto()))
                && l.resurssit().stream().anyMatch(r ->
                        vastaa(korvaa(r, p.konteksti()), p.resurssi()));
    }
    // @loppu arvioi

    private static final Pattern MUUTTUJA =
            Pattern.compile("\\$\\{([a-z.]+)}");

    /** ${avain} korvataan kontekstin arvolla; puuttuva ei osu mihinkään. */
    static String korvaa(String kaava, Map<String, String> konteksti) {
        Matcher m = MUUTTUJA.matcher(kaava);
        StringBuilder sb = new StringBuilder();
        while (m.find()) {
            String arvo = konteksti.get(m.group(1));
            m.appendReplacement(sb, Matcher.quoteReplacement(
                    arvo == null ? "\u0000" : arvo));
        }
        return m.appendTail(sb).toString();
    }

    /** Jokerimerkit: * mikä tahansa jono, ? yksi merkki. */
    static boolean vastaa(String kaava, String arvo) {
        StringBuilder re = new StringBuilder();
        for (char c : kaava.toCharArray()) {
            switch (c) {
                case '*' -> re.append(".*");
                case '?' -> re.append('.');
                default -> re.append(Pattern.quote(String.valueOf(c)));
            }
        }
        return arvo.matches(re.toString());
    }
}
