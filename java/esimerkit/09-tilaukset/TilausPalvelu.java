package fi.esimerkki.tilaus;

import java.time.Clock;
import java.time.Duration;
import java.util.List;
import java.util.Objects;

/** Sovelluslogiikka. Riippuvuudet tulevat konstruktorin kautta. */
public final class TilausPalvelu {
    private final Varasto varasto;
    private final Clock kello;
    private int seuraavaNumero = 1000;

    public TilausPalvelu(Varasto varasto, Clock kello) {
        this.varasto = Objects.requireNonNull(varasto);
        this.kello = Objects.requireNonNull(kello);
    }

    public Tilaus luo(String asiakas, long senttia) {
        var tilaus = new Tilaus(seuraavaNumero++, asiakas, senttia,
                kello.instant());
        varasto.tallenna(tilaus);
        return tilaus;
    }

    /** Tilaukset, jotka ovat vanhempia kuin annettu ikä. */
    public List<Tilaus> vanhentuneet(Duration ika) {
        var raja = kello.instant().minus(ika);
        return varasto.kaikki().stream()
                .filter(t -> t.luotu().isBefore(raja))
                .toList();
    }
}
