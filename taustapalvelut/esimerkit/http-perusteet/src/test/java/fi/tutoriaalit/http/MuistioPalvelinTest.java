package fi.tutoriaalit.http;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpRequest.BodyPublishers;
import java.net.http.HttpResponse;
import java.net.http.HttpResponse.BodyHandlers;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class MuistioPalvelinTest {

    private MuistioPalvelin palvelin;
    private final HttpClient asiakas = HttpClient.newHttpClient();

    @BeforeEach
    void kaynnista() throws IOException {
        palvelin = new MuistioPalvelin(0);     // 0 = vapaa portti
        palvelin.kaynnista();
    }

    @AfterEach
    void pysayta() {
        palvelin.close();
    }

    private URI osoite(String polku) {
        return URI.create("http://127.0.0.1:" + palvelin.portti() + polku);
    }

    private HttpResponse<String> laheta(HttpRequest.Builder pyynto)
            throws IOException, InterruptedException {
        return asiakas.send(pyynto.build(), BodyHandlers.ofString());
    }

    private HttpRequest.Builder teksti(String polku, String metodi,
            String runko) {
        return HttpRequest.newBuilder(osoite(polku))
                .header("Content-Type", "text/plain; charset=utf-8")
                .method(metodi, BodyPublishers.ofString(runko));
    }

    // @alku luonti
    @Test
    void postLuoUudenJaKertooSijainnin() throws Exception {
        var vastaus = laheta(teksti("/muistiot", "POST", "Osta maitoa"));

        assertThat(vastaus.statusCode()).isEqualTo(201);
        assertThat(vastaus.headers().firstValue("Location"))
                .hasValue("/muistiot/1");

        var haku = laheta(HttpRequest.newBuilder(osoite("/muistiot/1")));
        assertThat(haku.statusCode()).isEqualTo(200);
        assertThat(haku.body()).isEqualTo("Osta maitoa\n");
    }
    // @loppu luonti

    // @alku idempotenssi
    @Test
    void putOnIdempotenttiMuttaPostEi() throws Exception {
        var eka = laheta(teksti("/muistiot/kauppa", "PUT", "maito"));
        var toka = laheta(teksti("/muistiot/kauppa", "PUT", "maito"));
        assertThat(eka.statusCode()).isEqualTo(201);    // luotiin
        assertThat(toka.statusCode()).isEqualTo(200);   // korvattiin
        // Toisto ei muuttanut sisältöä: tila on sama kuin yhden jälkeen.

        laheta(teksti("/muistiot", "POST", "leipä"));
        laheta(teksti("/muistiot", "POST", "leipä"));
        var lista = laheta(HttpRequest.newBuilder(osoite("/muistiot")));
        assertThat(lista.body().lines()).containsExactly(
                "1: leipä", "2: leipä", "kauppa: maito");
    }
    // @loppu idempotenssi

    // @alku neuvottelu
    @Test
    void sisaltoneuvotteluValitseeEsitysmuodon() throws Exception {
        laheta(teksti("/muistiot/a", "PUT", "rivi \"lainattu\""));

        var json = laheta(HttpRequest.newBuilder(osoite("/muistiot/a"))
                .header("Accept", "application/json"));
        assertThat(json.headers().firstValue("Content-Type"))
                .hasValue("application/json; charset=utf-8");
        assertThat(json.body()).isEqualTo(
                "{\"id\":\"a\",\"teksti\":\"rivi \\\"lainattu\\\"\"}");

        var xml = laheta(HttpRequest.newBuilder(osoite("/muistiot/a"))
                .header("Accept", "application/xml"));
        assertThat(xml.statusCode()).isEqualTo(406);   // Not Acceptable
    }
    // @loppu neuvottelu

    // @alku ehdolliset
    @Test
    void etagEstaaTuplasiirronJaKadonneenPaivityksen() throws Exception {
        var luotu = laheta(teksti("/muistiot/b", "PUT", "versio 1"));
        String etag = luotu.headers().firstValue("ETag").orElseThrow();

        // Välimuistin uudelleenvalidointi: ei runkoa, jos ennallaan.
        var ennallaan = laheta(HttpRequest.newBuilder(osoite("/muistiot/b"))
                .header("If-None-Match", etag));
        assertThat(ennallaan.statusCode()).isEqualTo(304);
        assertThat(ennallaan.body()).isEmpty();

        // Kaksi asiakasta lukee version 1; ensimmäinen tallentaa.
        var anna = laheta(teksti("/muistiot/b", "PUT", "Annan muutos")
                .header("If-Match", etag));
        assertThat(anna.statusCode()).isEqualTo(200);

        // Toisen asiakkaan muutos perustuu vanhaan versioon: hylätään.
        var pekka = laheta(teksti("/muistiot/b", "PUT", "Pekan muutos")
                .header("If-Match", etag));
        assertThat(pekka.statusCode()).isEqualTo(412);
    }
    // @loppu ehdolliset

    // @alku virheet
    @Test
    void virheellisetPyynnot() throws Exception {
        var tyyppi = laheta(HttpRequest.newBuilder(osoite("/muistiot"))
                .header("Content-Type", "application/json")
                .POST(BodyPublishers.ofString("{}")));
        assertThat(tyyppi.statusCode()).isEqualTo(415);

        var metodi = laheta(HttpRequest.newBuilder(osoite("/muistiot"))
                .DELETE());
        assertThat(metodi.statusCode()).isEqualTo(405);
        assertThat(metodi.headers().firstValue("Allow"))
                .hasValue("GET, POST");

        var puuttuu = laheta(HttpRequest.newBuilder(osoite("/muistiot/x")));
        assertThat(puuttuu.statusCode()).isEqualTo(404);
    }
    // @loppu virheet

    @Test
    void deletePoistaaJaToistoKertooPuuttuvasta() throws Exception {
        laheta(teksti("/muistiot/c", "PUT", "poistettava"));
        var eka = laheta(HttpRequest.newBuilder(osoite("/muistiot/c"))
                .DELETE());
        var toka = laheta(HttpRequest.newBuilder(osoite("/muistiot/c"))
                .DELETE());
        assertThat(eka.statusCode()).isEqualTo(204);
        assertThat(toka.statusCode()).isEqualTo(404);
    }
}
