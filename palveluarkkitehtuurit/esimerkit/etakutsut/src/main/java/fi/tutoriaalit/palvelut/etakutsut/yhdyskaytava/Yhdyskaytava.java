package fi.tutoriaalit.palvelut.etakutsut.yhdyskaytava;

import com.sun.net.httpserver.HttpExchange;
import fi.tutoriaalit.palvelut.etakutsut.Palvelin;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpTimeoutException;
import java.time.Duration;
import java.util.Comparator;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * API-yhdyskäytävä: yksi sisäänkäynti usealle palvelulle. Hoitaa
 * yhteiset asiat yhdessä paikassa: todennuksen, pyyntörajoituksen,
 * korrelaatiotunnuksen, reitityksen ja aikarajat.
 */
public final class Yhdyskaytava {
    static final String KORRELAATIO = "X-Correlation-Id";
    private final HttpClient http = HttpClient.newHttpClient();
    private final Map<String, URI> reitit;      // polun alku -> palvelu
    private final Set<String> avaimet;
    private final Rajoitin rajoitin;
    private final Duration aikaraja;

    private Yhdyskaytava(Map<String, URI> reitit, Set<String> avaimet,
                         Rajoitin rajoitin, Duration aikaraja) {
        this.reitit = reitit;
        this.avaimet = avaimet;
        this.rajoitin = rajoitin;
        this.aikaraja = aikaraja;
    }

    public static Palvelin kaynnista(Map<String, URI> reitit,
                                     Set<String> avaimet,
                                     Rajoitin rajoitin,
                                     Duration aikaraja) {
        var y = new Yhdyskaytava(reitit, avaimet, rajoitin, aikaraja);
        return Palvelin.kaynnista(y::kasittele);
    }

    // @alku kasittele
    private void kasittele(HttpExchange vaihto) throws IOException {
        String avain = avain(vaihto);
        if (avain == null || !avaimet.contains(avain)) {
            Palvelin.vastaa(vaihto, 401, "{\"title\": \"Ei todennettu\"}");
            return;
        }
        if (!rajoitin.salli(avain)) {
            vaihto.getResponseHeaders().set("Retry-After", "1");
            Palvelin.vastaa(vaihto, 429, "{\"title\": \"Liikaa pyyntöjä\"}");
            return;
        }
        String polku = vaihto.getRequestURI().getPath();
        var reitti = reitit.keySet().stream()
            .filter(polku::startsWith)
            .max(Comparator.comparingInt(String::length));
        if (reitti.isEmpty()) {
            Palvelin.vastaa(vaihto, 404, "{\"title\": \"Ei reittiä\"}");
            return;
        }
        String tunnus = vaihto.getRequestHeaders().getFirst(KORRELAATIO);
        if (tunnus == null) {
            tunnus = UUID.randomUUID().toString();
        }
        vaihto.getResponseHeaders().set(KORRELAATIO, tunnus);
        valita(vaihto, reitit.get(reitti.get()).resolve(polku), tunnus);
    }
    // @loppu kasittele

    private void valita(HttpExchange vaihto, URI kohde, String tunnus)
            throws IOException {
        var pyynto = HttpRequest.newBuilder(kohde)
            .timeout(aikaraja)
            .header(KORRELAATIO, tunnus)
            .method(vaihto.getRequestMethod(),
                    HttpRequest.BodyPublishers.ofString(
                            Palvelin.runko(vaihto)))
            .build();
        try {
            var vastaus = http.send(pyynto,
                    HttpResponse.BodyHandlers.ofString());
            Palvelin.vastaa(vaihto, vastaus.statusCode(), vastaus.body());
        } catch (HttpTimeoutException e) {
            Palvelin.vastaa(vaihto, 504, "{\"title\": \"Aikakatkaisu\"}");
        } catch (IOException e) {
            Palvelin.vastaa(vaihto, 502, "{\"title\": \"Ei yhteyttä\"}");
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            Palvelin.vastaa(vaihto, 503, "{}");
        }
    }

    private static String avain(HttpExchange vaihto) {
        String otsake = vaihto.getRequestHeaders().getFirst("Authorization");
        return otsake != null && otsake.startsWith("Bearer ")
            ? otsake.substring("Bearer ".length()) : null;
    }
}
