package fi.tutoriaalit.kauppa.tilaus;

import java.time.Instant;
import java.util.List;
import org.springframework.data.annotation.Id;
import org.springframework.data.relational.core.mapping.MappedCollection;
import org.springframework.data.relational.core.mapping.Table;

// @alku tilaus
/**
 * Tilaus-aggregaatti: juuri ja sen rivit tallennetaan ja ladataan
 * yhdessä. Rivit ovat luettelo, ja niiden järjestys on sarakkeessa rivi.
 */
@Table("tilaus")
public record Tilaus(
        @Id Long id,
        String asiakas,
        Instant luotu,
        @MappedCollection(idColumn = "tilaus", keyColumn = "rivi")
        List<TilausRivi> rivit) {

    public long summaSentteina() {
        return rivit.stream()
                .mapToLong(r -> r.hintaSentteina() * r.maara())
                .sum();
    }

    Tilaus withId(Long uusiId) {
        return new Tilaus(uusiId, asiakas, luotu, rivit);
    }
}
// @loppu tilaus
