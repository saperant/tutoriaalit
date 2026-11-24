package fi.tutoriaalit.kauppa.tilaus;

import static org.assertj.core.api.Assertions.assertThat;

import fi.tutoriaalit.kauppa.tilaus.TilausOhjain.TilausVastaus;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.ArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.resttestclient.autoconfigure.*;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.client.RestTestClient;

// @alku asetelma
/**
 * Integraatiotesti: koko sovellus käynnistetään satunnaiseen porttiin,
 * ja pyynnöt kulkevat oikean HTTP:n, turvaketjun, transaktioiden ja
 * tietokannan läpi.
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureRestTestClient
@ActiveProfiles("test")
class TilausIntegraatioTest {

    @Autowired
    RestTestClient http;

    @Autowired
    JdbcClient jdbc;

    private long tuote(String nimi, int saldo) {
        jdbc.sql("UPDATE tuote SET saldo = :s WHERE nimi = :n")
                .param("s", saldo).param("n", nimi).update();
        return jdbc.sql("SELECT id FROM tuote WHERE nimi = :n")
                .param("n", nimi).query(Long.class).single();
    }

    private int saldo(long id) {
        return jdbc.sql("SELECT saldo FROM tuote WHERE id = :id")
                .param("id", id).query(Integer.class).single();
    }

    private RestTestClient.ResponseSpec tilaa(String kuka, String avain,
            String runko) {
        var pyynto = http.post().uri("/api/v1/tilaukset")
                .headers(h -> h.setBasicAuth(kuka, kuka + "-salasana"));
        if (avain != null) {
            pyynto = pyynto.header("Idempotency-Key", avain);
        }
        return pyynto.contentType(MediaType.APPLICATION_JSON)
                .body(runko).exchange();
    }

    private static String rivi(long tuote, int maara) {
        return "{\"rivit\": [{\"tuoteId\": %d, \"maara\": %d}]}"
                .formatted(tuote, maara);
    }
    // @loppu asetelma

    // @alku idempotenssi
    @Test
    void toistettuPyyntoSamallaAvaimellaEiTilaaKahdesti() {
        long kahvi = tuote("Kahvipavut 500 g", 100);

        var eka = tilaa("aino", "a7f3-tilaus-1", rivi(kahvi, 2))
                .expectStatus().isCreated()
                .expectBody(TilausVastaus.class).returnResult()
                .getResponseBody();
        // Yhteys katkesi ennen vastausta; asiakas lähettää uudelleen.
        var toka = tilaa("aino", "a7f3-tilaus-1", rivi(kahvi, 2))
                .expectBody(TilausVastaus.class).returnResult()
                .getResponseBody();

        assertThat(toka.id()).isEqualTo(eka.id());
        assertThat(saldo(kahvi)).isEqualTo(98);        // vähennetty kerran
        assertThat(eka.summaSentteina()).isEqualTo(2 * 1290);
    }
    // @loppu idempotenssi

    // @alku atomisuus
    @Test
    void epaonnistunutTilausPeruuKaikkiRivit() {
        long vaahdotin = tuote("Maitovaahdotin", 10);
        long kuppi = tuote("Kahvikuppi", 3);
        String runko = """
                {"rivit": [{"tuoteId": %d, "maara": 1},
                           {"tuoteId": %d, "maara": 5}]}
                """.formatted(vaahdotin, kuppi);

        tilaa("aino", null, runko)
                .expectStatus().isEqualTo(HttpStatus.CONFLICT)
                .expectHeader()
                .contentType(MediaType.APPLICATION_PROBLEM_JSON)
                .expectBody()
                .jsonPath("$.type")
                .isEqualTo("https://kauppa.example/ongelmat/saldo")
                .jsonPath("$.title").isEqualTo("Conflict")
                .jsonPath("$.detail")
                .isEqualTo("tuotteen " + kuppi + " saldo ei riitä")
                .jsonPath("$.tuote").isEqualTo(kuppi)
                .jsonPath("$.pyydetty").isEqualTo(5);

        // Ensimmäisen rivin varaus peruttiin transaktion mukana.
        assertThat(saldo(vaahdotin)).isEqualTo(10);
        assertThat(saldo(kuppi)).isEqualTo(3);
    }
    // @loppu atomisuus

    // @alku kilpailu
    @Test
    void samanaikaisetTilauksetEivatYlitaSaldoa() throws Exception {
        long kuppi = tuote("Kahvikuppi", 3);

        var tulokset = new ArrayList<Future<HttpStatus>>();
        try (var saikeet = Executors.newVirtualThreadPerTaskExecutor()) {
            for (int i = 0; i < 10; i++) {
                tulokset.add(saikeet.submit(() -> HttpStatus.valueOf(
                        tilaa("pekka", null, rivi(kuppi, 1))
                                .returnResult().getStatus().value())));
            }
        }
        long onnistuneet = 0;
        for (var tulos : tulokset) {
            if (tulos.get() == HttpStatus.CREATED) {
                onnistuneet++;
            }
        }
        assertThat(onnistuneet).isEqualTo(3);
        assertThat(saldo(kuppi)).isZero();
    }
    // @loppu kilpailu

    // @alku omistaja
    @Test
    void tilauksenNakeeVainOmistajaJaYllapitaja() {
        long tee = tuote("Vihreä tee", 50);
        long id = tilaa("aino", null, rivi(tee, 1))
                .expectBody(TilausVastaus.class).returnResult()
                .getResponseBody().id();

        http.get().uri("/api/v1/tilaukset/{id}", id)
                .headers(h -> h.setBasicAuth("pekka", "pekka-salasana"))
                .exchange().expectStatus().isForbidden();
        http.get().uri("/api/v1/tilaukset/{id}", id)
                .headers(h -> h.setBasicAuth("yllapito", "yllapito-salasana"))
                .exchange().expectStatus().isOk();
        http.get().uri("/api/v1/tilaukset/{id}", id)
                .exchange().expectStatus().isUnauthorized();
        http.get().uri("/api/v1/tilaukset/{id}", id)
                .headers(h -> h.setBasicAuth("aino", "väärä"))
                .exchange().expectStatus().isUnauthorized();
    }
    // @loppu omistaja

    // @alku havainnointi
    @Test
    void korrelaatiotunnusJaTerveystarkistus(@Autowired MeterRegistry m) {
        http.get().uri("/actuator/health")
                .header("X-Correlation-Id", "testi-123")
                .exchange()
                .expectStatus().isOk()
                .expectHeader().valueEquals("X-Correlation-Id", "testi-123")
                .expectBody().jsonPath("$.status").isEqualTo("UP");

        double ennen = m.counter("kauppa.tilaukset").count();
        tilaa("aino", null, rivi(tuote("Vihreä tee", 50), 1))
                .expectStatus().isCreated()
                .expectHeader().exists("X-Correlation-Id");
        assertThat(m.counter("kauppa.tilaukset").count())
                .isEqualTo(ennen + 1);
    }
    // @loppu havainnointi

    @Test
    void raporttiOnVainYllapitajalle() {
        http.get().uri("/api/v1/raportit/myynti")
                .headers(h -> h.setBasicAuth("aino", "aino-salasana"))
                .exchange().expectStatus().isForbidden();
        http.get().uri("/api/v1/raportit/myynti")
                .headers(h -> h.setBasicAuth("yllapito", "yllapito-salasana"))
                .exchange().expectStatus().isOk();
    }
}
