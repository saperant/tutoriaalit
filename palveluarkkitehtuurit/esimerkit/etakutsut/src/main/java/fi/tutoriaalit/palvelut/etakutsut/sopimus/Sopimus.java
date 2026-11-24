package fi.tutoriaalit.palvelut.etakutsut.sopimus;

import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.util.List;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/**
 * Kuluttajavetoinen sopimus: kuluttaja kirjaa, mitä pyyntöjä se tekee
 * ja mitä vastauksista se tarvitsee. Tuottaja ajaa samat pyynnöt omaa
 * toteutustaan vastaan.
 */
public record Sopimus(String kuluttaja, String tuottaja,
                      List<Vuorovaikutus> vuorovaikutukset) {

    public record Vuorovaikutus(String kuvaus, String tila,
                                Pyynto pyynto, Vastaus vastaus) {
    }

    public record Pyynto(String metodi, String polku) {
    }

    public record Vastaus(int tila, JsonNode runko) {
    }

    public static Sopimus lue(InputStream sisaan) {
        try (sisaan) {
            return new JsonMapper().readValue(sisaan, Sopimus.class);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
}
