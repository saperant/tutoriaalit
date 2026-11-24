package fi.tutoriaalit.palvelut.viestit.myynti;

import fi.tutoriaalit.palvelut.viestit.yhteinen.Viesti;
import jakarta.jms.JMSException;
import jakarta.jms.Message;
import java.math.BigDecimal;
import java.util.Map;
import java.util.Optional;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/**
 * Orkestroitu saga: myynti ohjaa tilauksen vaiheita komennoilla ja
 * reagoi vastauksiin. Jokainen siirtymä on yksi paikallinen transaktio,
 * jossa tila muuttuu ja seuraava komento kirjoitetaan lähteviin.
 */
@Component
class TilausSaga {
    private final JdbcClient jdbc;
    private final Lahtevat lahtevat;

    TilausSaga(JdbcClient jdbc, Lahtevat lahtevat) {
        this.jdbc = jdbc;
        this.lahtevat = lahtevat;
    }

    // @alku saga
    @JmsListener(destination = "myynti.vastaukset",
                 containerFactory = "jonot")
    @Transactional
    public void kunVastaus(Message jms) throws JMSException {
        Viesti v = Viesti.lue(jms);
        long id = Long.parseLong(v.korrelaatio());
        Optional<Tila> tila = jdbc.sql(
                "SELECT tila FROM myynti.tilaus WHERE id = ? FOR UPDATE")
            .param(id).query(Tila.class).optional();
        if (tila.isEmpty()) {
            return;                          // ei meidän tilauksemme
        }
        switch (tila.get() + "/" + v.tyyppi()) {
            case "ALOITETTU/VARATTU" -> {
                siirry(id, Tila.VARATTU);
                lahtevat.lisaa("maksut.komennot", "VELOITA", id,
                        Viesti.json(Map.of("summa", summa(id))));
            }
            case "ALOITETTU/VARAUS_EPAONNISTUI" -> siirry(id, Tila.PERUTTU);
            case "VARATTU/MAKSETTU" -> {
                siirry(id, Tila.VAHVISTETTU);
                lahtevat.lisaa("aihe:tilaukset.tapahtumat",
                        "TilausVahvistettu", id, "{}");
            }
            case "VARATTU/MAKSU_HYLATTY" -> {
                // Kompensaatio: varaus perutaan.
                siirry(id, Tila.PERUUTETAAN);
                lahtevat.lisaa("varasto.komennot", "VAPAUTA", id, "{}");
            }
            case "PERUUTETAAN/VAPAUTETTU" -> siirry(id, Tila.PERUTTU);
            default -> {
                // Toistettu tai myöhästynyt vastaus: ei tehdä mitään.
            }
        }
    }
    // @loppu saga

    private void siirry(long id, Tila uusi) {
        jdbc.sql("UPDATE myynti.tilaus SET tila = ? WHERE id = ?")
            .params(uusi.name(), id).update();
    }

    private BigDecimal summa(long id) {
        return jdbc.sql("SELECT summa FROM myynti.tilaus WHERE id = ?")
            .param(id).query(BigDecimal.class).single();
    }
}
