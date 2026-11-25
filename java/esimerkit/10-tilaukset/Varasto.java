package fi.esimerkki.tilaus;

import java.util.List;
import java.util.Optional;

/** Tilausten tallennus. Toteutus valitaan kokoonpanossa. */
public interface Varasto {
    void tallenna(Tilaus tilaus);

    Optional<Tilaus> hae(int numero);

    List<Tilaus> kaikki();
}
