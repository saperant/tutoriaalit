package fi.tutoriaalit.palvelut.uudistus.uusi;

import com.sun.net.httpserver.HttpServer;
import fi.tutoriaalit.palvelut.uudistus.Http;

/** Uusi palvelu: GET /asiakkaat/{id} JSONina. Tieto on vielä vanhassa
 *  järjestelmässä, ja se luetaan korruption estokerroksen kautta. */
public final class Asiakaspalvelu {
    private Asiakaspalvelu() {
    }

    public static HttpServer kaynnista(Korruptionestokerros vanha) {
        return Http.palvelin(vaihto -> {
            String id = vaihto.getRequestURI().getPath()
                .substring("/asiakkaat/".length());
            var vastaus = vanha.asiakas(id)
                .map(a -> new Http.Vastaus(200, "application/json",
                        a.json()))
                .orElse(new Http.Vastaus(404, "application/json",
                        "{\"title\": \"Ei asiakasta\"}"));
            Http.vastaa(vaihto, vastaus);
        });
    }
}
