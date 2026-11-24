package fi.tutoriaalit.palvelut.viestit.integraatio;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.TreeMap;
import java.util.function.Function;
import java.util.function.Predicate;

/**
 * Integraatiomallit (Enterprise Integration Patterns) pieninä funktioina.
 * Kehykset kuten Apache Camel ja Spring Integration tarjoavat samat
 * mallit valmiina ja kytkevät ne oikeisiin kanaviin.
 */
public final class Mallit {
    private Mallit() {
    }

    // @alku kaantaja
    /** Kääntäjä (Message Translator): vanhan järjestelmän rivi
     *  "TILAUS;T-1;FI;kahvinkeitin:1,suodatin:3" yhteiseen muotoon. */
    public static Sanoma kaanna(String rivi) {
        String[] osat = rivi.split(";");
        if (osat.length != 4 || !osat[0].equals("TILAUS")) {
            throw new IllegalArgumentException("tuntematon muoto: " + rivi);
        }
        return new Sanoma(Map.of("tilaus", osat[1], "maa", osat[2]),
                osat[3]);
    }
    // @loppu kaantaja

    // @alku pilkkoja
    /** Pilkkoja (Splitter): tilauksesta rivikohtaiset viestit. Jokaisessa
     *  on korrelaatiotunnus ja tieto siitä, montako osaa on yhteensä. */
    public static List<Sanoma> pilko(Sanoma tilaus) {
        String[] rivit = tilaus.runko().split(",");
        var osat = new ArrayList<Sanoma>();
        for (int i = 0; i < rivit.length; i++) {
            osat.add(new Sanoma(Map.of(
                    "korrelaatio", tilaus.otsake("tilaus"),
                    "maa", tilaus.otsake("maa"),
                    "osa", String.valueOf(i + 1),
                    "osia", String.valueOf(rivit.length)), rivit[i]));
        }
        return osat;
    }
    // @loppu pilkkoja

    // @alku reititin
    /** Sisältöön perustuva reititin (Content-Based Router). */
    public static Function<Sanoma, String> reititin(
            Map<String, String> maaKanava, String oletus) {
        return s -> maaKanava.getOrDefault(s.otsake("maa"), oletus);
    }

    /** Suodatin (Message Filter). */
    public static Predicate<Sanoma> eiNollarivia() {
        return s -> !s.runko().endsWith(":0");
    }
    // @loppu reititin

    // @alku kokooja
    /** Kokooja (Aggregator): kerää saman korrelaatiotunnuksen osat ja
     *  julkaisee koosteen, kun kaikki osat ovat saapuneet. Osat voivat
     *  tulla missä järjestyksessä tahansa. */
    public static final class Kokooja {
        private final Map<String, Map<Integer, String>> kesken =
            new HashMap<>();

        public Optional<Sanoma> vastaanota(Sanoma osa) {
            String tunnus = osa.otsake("korrelaatio");
            var osat = kesken.computeIfAbsent(tunnus, k -> new HashMap<>());
            osat.put(Integer.valueOf(osa.otsake("osa")), osa.runko());
            if (osat.size() < Integer.parseInt(osa.otsake("osia"))) {
                return Optional.empty();
            }
            kesken.remove(tunnus);
            String runko = String.join(",", new TreeMap<>(osat).values());
            return Optional.of(new Sanoma(
                    Map.of("korrelaatio", tunnus), runko));
        }
    }
    // @loppu kokooja
}
