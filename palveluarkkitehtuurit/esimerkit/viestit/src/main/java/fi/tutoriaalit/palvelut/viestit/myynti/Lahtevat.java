package fi.tutoriaalit.palvelut.viestit.myynti;

import java.util.UUID;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Component;

// @alku lahtevat
/**
 * Lähtevien viestien taulu (transactional outbox). Viesti kirjoitetaan
 * tauluun samassa tietokantatransaktiossa kuin tilan muutos, joten
 * molemmat tallentuvat tai kumpikaan ei. Välittäjä lähettää rivit
 * myöhemmin.
 */
@Component
class Lahtevat {
    private final JdbcClient jdbc;

    Lahtevat(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    void lisaa(String kohde, String tyyppi, long tilausId, String runko) {
        jdbc.sql("""
                INSERT INTO myynti.lahtevat
                  (viesti_id, kohde, tyyppi, korrelaatio, runko)
                VALUES (?, ?, ?, ?, ?)""")
            .params(UUID.randomUUID().toString(), kohde, tyyppi,
                    String.valueOf(tilausId), runko)
            .update();
    }
}
// @loppu lahtevat
