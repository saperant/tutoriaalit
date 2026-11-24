package fi.tutoriaalit.palvelut.etakutsut.yhdyskaytava;

import static org.assertj.core.api.Assertions.assertThat;

import fi.tutoriaalit.palvelut.etakutsut.Palvelin;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicLong;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class YhdyskaytavaTest {
    final HttpClient http = HttpClient.newHttpClient();
    final AtomicLong kello = new AtomicLong();
    Palvelin varasto;
    Palvelin myynti;
    Palvelin yhdyskaytava;

    @BeforeEach
    void kaynnista() {
        // Palvelut kertovat nimensä ja saamansa korrelaatiotunnuksen.
        varasto = Palvelin.kaynnista(v -> Palvelin.vastaa(v, 200,
                "\"varasto " + v.getRequestHeaders()
                    .getFirst("X-Correlation-Id") + "\""));
        myynti = Palvelin.kaynnista(v -> Palvelin.vastaa(v, 200,
                "\"myynti\""));
        // @alku kaynnistys
        var reitit = Map.of(
                "/varasto/", varasto.osoite(),
                "/tilaukset/", myynti.osoite());
        var rajoitin = new Rajoitin(3, 1.0, kello::get);
        yhdyskaytava = Yhdyskaytava.kaynnista(reitit, Set.of("avain-1"),
                rajoitin, Duration.ofMillis(500));
        // @loppu kaynnistys
    }

    @AfterEach
    void sammuta() {
        yhdyskaytava.close();
        varasto.close();
        myynti.close();
    }

    HttpResponse<String> hae(String polku, String avain) throws Exception {
        var pyynto = HttpRequest.newBuilder(
                yhdyskaytava.osoite().resolve(polku))
            .header("X-Correlation-Id", "k-17");
        if (avain != null) {
            pyynto.header("Authorization", "Bearer " + avain);
        }
        return http.send(pyynto.build(),
                HttpResponse.BodyHandlers.ofString());
    }

    // @alku testit
    @Test
    void reititysJaKorrelaatiotunnus() throws Exception {
        assertThat(hae("/varasto/saldo/x", "avain-1").body())
            .isEqualTo("\"varasto k-17\"");
        assertThat(hae("/tilaukset/1", "avain-1").body())
            .isEqualTo("\"myynti\"");
        assertThat(hae("/muu", "avain-1").statusCode()).isEqualTo(404);
    }

    @Test
    void ilmanAvaintaEiPaaseSisaan() throws Exception {
        assertThat(hae("/varasto/saldo/x", null).statusCode())
            .isEqualTo(401);
        assertThat(hae("/varasto/saldo/x", "vaara").statusCode())
            .isEqualTo(401);
    }

    @Test
    void rajoitinSalliiPurskeenMuttaEiTulvaa() throws Exception {
        for (int i = 0; i < 3; i++) {
            assertThat(hae("/tilaukset/1", "avain-1").statusCode())
                .isEqualTo(200);
        }
        var neljas = hae("/tilaukset/1", "avain-1");
        assertThat(neljas.statusCode()).isEqualTo(429);
        assertThat(neljas.headers().firstValue("Retry-After"))
            .hasValue("1");
        kello.addAndGet(1_000_000_000L);       // sekunti kuluu
        assertThat(hae("/tilaukset/1", "avain-1").statusCode())
            .isEqualTo(200);
    }
    // @loppu testit

    @Test
    void kaatunutPalveluOn502() throws Exception {
        varasto.close();
        assertThat(hae("/varasto/saldo/x", "avain-1").statusCode())
            .isEqualTo(502);
    }

    @Test
    void hidasPalveluOn504() throws Exception {
        try (var hidas = Palvelin.kaynnista(v -> {
                try {
                    Thread.sleep(2000);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                Palvelin.vastaa(v, 200, "{}");
            });
            var y = Yhdyskaytava.kaynnista(
                Map.of("/", hidas.osoite()), Set.of("avain-1"),
                new Rajoitin(3, 1.0, kello::get), Duration.ofMillis(100))) {
            var pyynto = HttpRequest.newBuilder(y.osoite().resolve("/x"))
                .header("Authorization", "Bearer avain-1").build();
            assertThat(http.send(pyynto, HttpResponse.BodyHandlers
                    .ofString()).statusCode()).isEqualTo(504);
        }
    }
}
