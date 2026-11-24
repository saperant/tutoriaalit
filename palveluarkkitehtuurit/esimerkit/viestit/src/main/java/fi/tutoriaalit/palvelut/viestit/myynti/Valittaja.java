package fi.tutoriaalit.palvelut.viestit.myynti;

import fi.tutoriaalit.palvelut.viestit.yhteinen.Lahettaja;
import java.util.List;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

// @alku valittaja
/**
 * Lähettää lähtevien viestien taulun rivit välittäjälle järjestyksessä
 * ja merkitsee ne lähetetyiksi. Jos prosessi kaatuu lähetyksen ja
 * merkinnän välissä, rivi lähetetään uudelleen: toimitus on "vähintään
 * kerran", ja vastaanottajien on siksi oltava idempotentteja.
 */
@Component
class Valittaja {
    record Rivi(long id, String viestiId, String kohde, String tyyppi,
                String korrelaatio, String runko) {
    }

    private final JdbcClient jdbc;
    private final Lahettaja lahettaja;

    Valittaja(JdbcClient jdbc, Lahettaja lahettaja) {
        this.jdbc = jdbc;
        this.lahettaja = lahettaja;
    }

    @Scheduled(fixedDelay = 50)
    void valita() {
        List<Rivi> rivit = jdbc.sql("""
                SELECT id, viesti_id, kohde, tyyppi, korrelaatio, runko
                FROM myynti.lahtevat WHERE lahetetty IS NULL
                ORDER BY id LIMIT 100""")
            .query(Rivi.class).list();
        for (Rivi r : rivit) {
            lahettaja.laheta(r.kohde(), r.viestiId(), r.tyyppi(),
                    r.korrelaatio(), r.runko());
            jdbc.sql("""
                    UPDATE myynti.lahtevat SET lahetetty = LOCALTIMESTAMP
                    WHERE id = ?""")
                .param(r.id()).update();
        }
    }
}
// @loppu valittaja
