package fi.tutoriaalit.palvelut.viestit.yhteinen;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.jms.core.JmsTemplate;
import org.springframework.stereotype.Component;

/** Lähettää viestin jonoon tai aiheeseen. Kohde "aihe:x" on aihe. */
@Component
public class Lahettaja {
    private final JmsTemplate jonot;
    private final JmsTemplate aiheet;

    Lahettaja(JmsTemplate jmsTemplate,
              @Qualifier("aiheTemplate") JmsTemplate aiheet) {
        this.jonot = jmsTemplate;
        this.aiheet = aiheet;
    }

    public void laheta(String kohde, String id, String tyyppi,
                       String korrelaatio, String runko) {
        boolean aihe = kohde.startsWith("aihe:");
        (aihe ? aiheet : jonot).send(aihe ? kohde.substring(5) : kohde,
            istunto -> {
                var viesti = istunto.createTextMessage(runko);
                viesti.setStringProperty("viestiId", id);
                viesti.setStringProperty("tyyppi", tyyppi);
                viesti.setStringProperty("korrelaatio", korrelaatio);
                return viesti;
            });
    }
}
