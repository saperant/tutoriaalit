package fi.tutoriaalit.palvelut.uudistus.vanha;

import com.sun.net.httpserver.HttpServer;
import fi.tutoriaalit.palvelut.uudistus.Http;
import java.util.Map;

/**
 * Vanha järjestelmä (perintöjärjestelmä). Puhuu omaa kieltään:
 * puolipisteillä erotetut kentät, nimi isoilla kirjaimilla sukunimi
 * ensin, tila kirjainkoodina ja päivämäärä muodossa VVVVKKPP.
 *
 *   GET /asiakas?nro=1001  ->  1001;VIRTANEN AINO;A;20230115
 *   GET /laskut?nro=1001   ->  2;189,50
 */
public final class Asiakasrekisteri {
    private Asiakasrekisteri() {
    }

    public static HttpServer kaynnista(Map<String, String> rivit) {
        return Http.palvelin(vaihto -> {
            String kysely = vaihto.getRequestURI().getQuery();
            String nro = kysely == null ? "" : kysely.replace("nro=", "");
            String polku = vaihto.getRequestURI().getPath();
            String runko = switch (polku) {
                case "/asiakas" -> rivit.get(nro);
                case "/laskut" -> rivit.containsKey(nro) ? "2;189,50" : null;
                default -> null;
            };
            Http.vastaa(vaihto, runko == null
                    ? new Http.Vastaus(404, "text/plain", "EI LOYDY")
                    : new Http.Vastaus(200, "text/plain", runko));
        });
    }
}
