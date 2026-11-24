package fi.tutoriaalit.palveluturva.salaisuudet;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

/**
 * Salaisuusvarasto (Vaultin periaatteet pienoiskoossa): staattiset
 * salaisuudet polun mukaan, lukuoikeus identiteetin mukaan ja
 * dynaamiset tietokantatunnukset, joilla on vuokra-aika.
 */
public final class Salaisuusvarasto {

    // @alku dynaaminen
    /** Tunnus, joka on luotu yhdelle palvelulle ja vanhenee itsestään. */
    public record Tunnus(String vuokra, String kayttaja, String salasana,
                         String omistaja, Instant vanhenee) {}

    private final Map<String, Tunnus> vuokrat = new LinkedHashMap<>();

    public synchronized Tunnus luoTietokantatunnus(String identiteetti,
                                                   Duration ttl) {
        String id = HexFormat.of().formatHex(Avainpalvelu.satunnainen(4));
        var tunnus = new Tunnus("vuokra-" + id, "v-" + id,
                HexFormat.of().formatHex(Avainpalvelu.satunnainen(16)),
                identiteetti, kello.instant().plus(ttl));
        vuokrat.put(tunnus.vuokra(), tunnus);
        return tunnus;
    }

    /** Tietokanta kysyy tätä kirjautumisen yhteydessä. */
    public synchronized boolean kelpaa(String kayttaja, String salasana) {
        return vuokrat.values().stream().anyMatch(t ->
                t.kayttaja().equals(kayttaja)
                && t.salasana().equals(salasana)
                && kello.instant().isBefore(t.vanhenee()));
    }

    public synchronized void kumoa(String vuokra) {
        vuokrat.remove(vuokra);
    }

    /** Poikkeamassa: kaikki yhden palvelun tunnukset kerralla. */
    public synchronized int kumoaKaikki(String identiteetti) {
        int ennen = vuokrat.size();
        vuokrat.values().removeIf(t -> t.omistaja().equals(identiteetti));
        return ennen - vuokrat.size();
    }
    // @loppu dynaaminen

    // @alku staattinen
    private final Map<String, byte[]> salaisuudet = new LinkedHashMap<>();
    private final Map<String, Set<String>> luvat;
    private final Clock kello;

    /** @param luvat identiteetti → polkujen etuliitteet, joita se lukee */
    public Salaisuusvarasto(Map<String, Set<String>> luvat, Clock kello) {
        this.luvat = Map.copyOf(luvat);
        this.kello = kello;
    }

    public synchronized void kirjoita(String polku, byte[] arvo) {
        salaisuudet.put(polku, arvo.clone());
    }

    public synchronized Optional<byte[]> lue(String identiteetti,
                                             String polku) {
        boolean sallittu = luvat.getOrDefault(identiteetti, Set.of())
                .stream().anyMatch(polku::startsWith);
        return sallittu ? Optional.ofNullable(salaisuudet.get(polku))
                : Optional.empty();
    }
    // @loppu staattinen
}
