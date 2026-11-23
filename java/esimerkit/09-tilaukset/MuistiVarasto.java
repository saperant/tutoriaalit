package fi.esimerkki.tilaus;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.TreeMap;

/** Pakkauksen sisäinen toteutus: ei näy paketin ulkopuolelle. */
final class MuistiVarasto implements Varasto {
    private final Map<Integer, Tilaus> tilaukset = new TreeMap<>();

    @Override
    public void tallenna(Tilaus tilaus) {
        tilaukset.put(tilaus.numero(), tilaus);
    }

    @Override
    public Optional<Tilaus> hae(int numero) {
        return Optional.ofNullable(tilaukset.get(numero));
    }

    @Override
    public List<Tilaus> kaikki() {
        return List.copyOf(tilaukset.values());
    }
}
