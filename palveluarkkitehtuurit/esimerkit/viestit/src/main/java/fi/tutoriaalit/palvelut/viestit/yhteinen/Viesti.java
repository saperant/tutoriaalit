package fi.tutoriaalit.palvelut.viestit.yhteinen;

import jakarta.jms.JMSException;
import jakarta.jms.Message;
import jakarta.jms.TextMessage;
import java.util.Map;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/**
 * Viestin kirjekuori. Otsakkeet ovat JMS-ominaisuuksia: yksilöivä
 * {@code viestiId} (toistojen tunnistamiseen), {@code tyyppi} (mitä
 * viesti tarkoittaa) ja {@code korrelaatio} (mihin tilaukseen se liittyy).
 * Runko on JSONia.
 */
public record Viesti(String id, String tyyppi, String korrelaatio,
                     JsonNode runko) {
    public static final JsonMapper JSON = new JsonMapper();

    public static Viesti lue(Message viesti) throws JMSException {
        return new Viesti(viesti.getStringProperty("viestiId"),
                viesti.getStringProperty("tyyppi"),
                viesti.getStringProperty("korrelaatio"),
                JSON.readTree(((TextMessage) viesti).getText()));
    }

    public static String json(Map<String, ?> arvot) {
        return JSON.writeValueAsString(arvot);
    }
}
