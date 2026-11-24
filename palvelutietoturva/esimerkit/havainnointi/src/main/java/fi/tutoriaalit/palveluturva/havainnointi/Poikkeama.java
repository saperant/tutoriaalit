package fi.tutoriaalit.palveluturva.havainnointi;

import java.time.Instant;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

/** Havaitseminen, aikajana ja eristäminen tietoturvapoikkeamassa. */
public final class Poikkeama {

    // @alku havaitse
    /**
     * Poikkeava toiminta: palvelu tekee toimintoa, jota se ei ole
     * tehnyt perustasojaksolla. Palvelujen käytös on paljon
     * ennustettavampaa kuin ihmisten, joten tämä yksinkertainen sääntö
     * on palvelukokonaisuudessa tehokas.
     */
    public static List<Tapahtuma> poikkeavat(List<Tapahtuma> perustaso,
                                             List<Tapahtuma> uudet) {
        Map<String, Set<String>> tunnetut = perustaso.stream().collect(
                Collectors.groupingBy(Tapahtuma::toimija,
                        Collectors.mapping(Tapahtuma::toiminto,
                                Collectors.toSet())));
        return uudet.stream().filter(t -> !tunnetut
                .getOrDefault(t.toimija(), Set.of())
                .contains(t.toiminto())).toList();
    }
    // @loppu havaitse

    // @alku aikajana
    /** Yhden pyynnön kulku palvelujen läpi korrelaatiotunnisteella. */
    public static List<String> aikajana(String korrelaatio,
                                        List<List<Tapahtuma>> lokit) {
        return lokit.stream().flatMap(List::stream)
                .filter(t -> t.korrelaatio().equals(korrelaatio))
                .sorted(Comparator.comparing(Tapahtuma::aika))
                .map(t -> t.aika() + " " + t.palvelu() + ": "
                        + t.toiminto() + " " + t.resurssi() + " -> "
                        + t.tulos())
                .toList();
    }
    // @loppu aikajana

    // @alku eristys
    /** Kumoamislista: kumotut identiteetit ja tokenit (jti), joita
     *  jokainen palvelu tarkistaa ennen pyynnön käsittelyä. */
    public static final class Kumoamislista {
        private final Set<String> kumotut = new HashSet<>();
        private Instant viimeksiPaivitetty = Instant.EPOCH;

        public synchronized void kumoa(String tunniste, Instant aika) {
            kumotut.add(tunniste);
            viimeksiPaivitetty = aika;
        }

        public synchronized boolean kumottu(String tunniste) {
            return kumotut.contains(tunniste);
        }

        public synchronized Instant paivitetty() {
            return viimeksiPaivitetty;
        }
    }
    // @loppu eristys

    private Poikkeama() {}
}
