package fi.tutoriaalit.palveluturva.luottamus;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Map;
import javax.net.ssl.SSLContext;

/**
 * Esimerkkien HTTP-asiakas. Palauttaa tilakoodin ja rungon; jos
 * yhteys ei synny (esimerkiksi TLS-kättely hylätään), tila on 0.
 */
public final class Asiakas {

    public record Tulos(int tila, String runko) {
        @Override
        public String toString() {
            return tila == 0 ? "ei yhteyttä" : tila + " " + runko;
        }
    }

    private Asiakas() {}

    public static Tulos hae(SSLContext tls, URI osoite,
                            Map<String, String> otsakkeet) {
        // Uusi asiakas joka kerta: ei jaettua TLS-istuntoa, jolloin
        // jokainen kutsu tekee oman kättelyn.
        var rakentaja = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(5));
        if (tls != null) {
            rakentaja.sslContext(tls);
        }
        try (HttpClient http = rakentaja.build()) {
            var pyynto = HttpRequest.newBuilder(osoite);
            otsakkeet.forEach(pyynto::header);
            HttpResponse<String> v = http.send(pyynto.build(),
                    HttpResponse.BodyHandlers.ofString());
            return new Tulos(v.statusCode(), v.body());
        } catch (IOException e) {
            return new Tulos(0, e.getClass().getSimpleName());
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException(e);
        }
    }

    public static Tulos hae(SSLContext tls, URI osoite) {
        return hae(tls, osoite, Map.of());
    }
}
