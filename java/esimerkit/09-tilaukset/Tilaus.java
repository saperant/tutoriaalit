package fi.esimerkki.tilaus;

import java.time.Instant;
import java.util.Objects;

/** Tilaus on muuttumaton arvo. */
public record Tilaus(int numero, String asiakas, long senttia,
        Instant luotu) {

    public Tilaus {
        Objects.requireNonNull(asiakas, "asiakas");
        Objects.requireNonNull(luotu, "luotu");
        if (senttia <= 0) {
            throw new IllegalArgumentException("summan on oltava > 0");
        }
    }
}
