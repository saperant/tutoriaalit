package fi.tutoriaalit.palvelut.viestit.toimitus;

import fi.tutoriaalit.palvelut.viestit.yhteinen.Viesti;
import jakarta.jms.JMSException;
import jakarta.jms.Message;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/** Tilaa myynnin tapahtumat ja reagoi vahvistettuun tilaukseen. */
@Component
class ToimitusTilaaja {
    private final JdbcClient jdbc;

    ToimitusTilaaja(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    @JmsListener(destination = "tilaukset.tapahtumat",
                 containerFactory = "aiheet")
    @Transactional
    public void kunTapahtuma(Message jms) throws JMSException {
        Viesti v = Viesti.lue(jms);
        if (v.tyyppi().equals("TilausVahvistettu")) {
            // MERGE tekee käsittelystä idempotentin.
            jdbc.sql("MERGE INTO toimitus.lahetys KEY (tilaus_id) VALUES (?)")
                .param(v.korrelaatio()).update();
        }
    }
}
