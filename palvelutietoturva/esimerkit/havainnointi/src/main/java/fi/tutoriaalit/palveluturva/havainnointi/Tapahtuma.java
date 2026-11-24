package fi.tutoriaalit.palveluturva.havainnointi;

import java.time.Instant;
import java.util.Map;

// @alku tapahtuma
/**
 * Auditointitapahtuma: kuka teki mitä mille, milloin, minkä pyynnön
 * osana (korrelaatiotunniste) ja mikä oli lopputulos ja peruste.
 */
public record Tapahtuma(Instant aika, String korrelaatio, String palvelu,
                        String toimija, String toiminto, String resurssi,
                        String tulos, Map<String, String> tiedot) {
    public Tapahtuma {
        tiedot = Map.copyOf(tiedot);
    }
}
// @loppu tapahtuma
