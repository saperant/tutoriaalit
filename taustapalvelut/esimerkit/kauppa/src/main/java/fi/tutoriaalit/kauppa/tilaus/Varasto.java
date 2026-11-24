package fi.tutoriaalit.kauppa.tilaus;

import fi.tutoriaalit.kauppa.virheet.SaldoEiRiita;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Component;

// @alku varasto
/**
 * Saldon vähennys yhdellä ehdollisella UPDATE-lauseella. Tietokanta
 * lukitsee rivin päivityksen ajaksi, joten kaksi samanaikaista tilausta
 * eivät voi molemmat ottaa viimeistä kappaletta. Lue–tarkista–kirjoita
 * sovelluksessa olisi kilpatilanne.
 */
@Component
public class Varasto {

    private final JdbcClient jdbc;

    public Varasto(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    /** Vähentää saldoa tai heittää poikkeuksen, jos saldo ei riitä. */
    public void varaa(long tuoteId, int maara) {
        int muuttuneet = jdbc.sql("""
                UPDATE tuote
                   SET saldo = saldo - :maara, versio = versio + 1
                 WHERE id = :id AND saldo >= :maara
                """)
                .param("maara", maara)
                .param("id", tuoteId)
                .update();
        if (muuttuneet == 0) {
            throw new SaldoEiRiita(tuoteId, maara);
        }
    }
}
// @loppu varasto
