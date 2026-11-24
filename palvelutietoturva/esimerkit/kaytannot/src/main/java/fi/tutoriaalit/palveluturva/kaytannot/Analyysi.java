package fi.tutoriaalit.palveluturva.kaytannot;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

/**
 * Vähimpien oikeuksien analyysi: verrataan myönnettyjä oikeuksia
 * siihen, mitä palvelu on auditointilokin mukaan oikeasti tehnyt.
 */
public final class Analyysi {

    /** Auditointilokin rivi: toteutunut, sallittu pyyntö. */
    public record Kaytto(String toimija, String toiminto,
                         String resurssi) {}

    // @alku analyysi
    /** Lausekkeet, joita ei käytetty lainkaan tarkastelujaksolla. */
    public static List<String> kayttamattomat(Kaytanto kaytanto,
                                              List<Kaytto> loki) {
        List<String> tulos = new ArrayList<>();
        for (Kaytanto.Lauseke l : kaytanto.lausekkeet()) {
            boolean kaytetty = loki.stream().anyMatch(k -> Moottori.kohdistuu(
                    l, new Moottori.Pyynto(k.toimija(), k.toiminto(),
                            k.resurssi(), Map.of())));
            if (l.vaikutus() == Kaytanto.Vaikutus.SALLI && !kaytetty) {
                tulos.add(l.tunnus());
            }
        }
        return tulos;
    }

    /** Ehdotus: käytetyt toiminnot resurssityypeittäin. */
    public static Map<String, Set<String>> ehdotus(List<Kaytto> loki) {
        Map<String, Set<String>> tulos = new TreeMap<>();
        for (Kaytto k : loki) {
            String tyyppi = k.resurssi().replaceAll("/[^/]+$", "/*");
            tulos.computeIfAbsent(tyyppi, x -> new TreeSet<>())
                    .add(k.toiminto());
        }
        return tulos;
    }
    // @loppu analyysi

    private Analyysi() {}
}
