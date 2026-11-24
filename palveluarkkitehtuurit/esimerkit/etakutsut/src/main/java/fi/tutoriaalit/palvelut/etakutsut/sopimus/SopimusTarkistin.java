package fi.tutoriaalit.palvelut.etakutsut.sopimus;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** Tuottajan testeille: ajaa sopimuksen pyynnöt ja vertaa vastauksia. */
public final class SopimusTarkistin {
    private static final HttpClient HTTP = HttpClient.newHttpClient();
    private static final JsonMapper JSON = new JsonMapper();

    private SopimusTarkistin() {
    }

    // @alku tarkista
    /**
     * Palauttaa poikkeamat. Tila asetetaan ennen pyyntöä (esim. "tuote
     * on varastossa"). Vastauksesta tarkistetaan tilakoodi ja se, että
     * jokainen sopimuksen kenttä on olemassa ja samaa JSON-tyyppiä.
     * Arvojen ei tarvitse täsmätä, eivätkä ylimääräiset kentät haittaa:
     * kuluttaja sitoutuu vain siihen, mitä se käyttää.
     */
    public static List<String> tarkista(Sopimus sopimus, URI tuottaja,
                                        Map<String, Runnable> tilat)
            throws IOException, InterruptedException {
        var poikkeamat = new ArrayList<String>();
        for (var v : sopimus.vuorovaikutukset()) {
            tilat.getOrDefault(v.tila(), () -> { }).run();
            var pyynto = HttpRequest.newBuilder(
                    tuottaja.resolve(v.pyynto().polku()))
                .method(v.pyynto().metodi(),
                        HttpRequest.BodyPublishers.noBody())
                .build();
            var vastaus = HTTP.send(pyynto,
                    HttpResponse.BodyHandlers.ofString());
            if (vastaus.statusCode() != v.vastaus().tila()) {
                poikkeamat.add(v.kuvaus() + ": tila "
                        + vastaus.statusCode());
                continue;
            }
            vertaa(v.kuvaus(), v.vastaus().runko(),
                    JSON.readTree(vastaus.body()), poikkeamat);
        }
        return poikkeamat;
    }
    // @loppu tarkista

    private static void vertaa(String kuvaus, JsonNode odotettu,
                               JsonNode saatu, List<String> poikkeamat) {
        for (var kentta : odotettu.propertyNames()) {
            JsonNode arvo = saatu.get(kentta);
            if (arvo == null) {
                poikkeamat.add(kuvaus + ": kenttä puuttuu: " + kentta);
            } else if (arvo.getNodeType()
                    != odotettu.get(kentta).getNodeType()) {
                poikkeamat.add(kuvaus + ": väärä tyyppi: " + kentta);
            }
        }
    }
}
