package fi.tutoriaalit.kauppa.toimitus;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.junit.jupiter.api.Assertions.assertTimeout;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.web.client.HttpClientErrorException;

/** Asiakkaan testit JDK:n HttpServer-valepalvelinta vasten (luku 2). */
class ToimitusAsiakasTest {

    private static final Duration PITKA = Duration.ofSeconds(30);

    private HttpServer palvelin;
    private final AtomicInteger kutsuja = new AtomicInteger();
    private final CountDownLatch lopeta = new CountDownLatch(1);

    @BeforeEach
    void kaynnista() throws IOException {
        var osoite = new InetSocketAddress("127.0.0.1", 0);
        palvelin = HttpServer.create(osoite, 0);
        palvelin.setExecutor(Executors.newVirtualThreadPerTaskExecutor());
        palvelin.start();
    }

    @AfterEach
    void sammuta() {
        lopeta.countDown();
        palvelin.stop(0);
    }

    // @alku testit
    @Test
    void tilapainenVirheYritetaanUudelleen() {
        palvelin.createContext("/arviot/", pyynto -> {
            if (kutsuja.incrementAndGet() < 3) {
                vastaa(pyynto, 503, "");
            } else {
                vastaa(pyynto, 200,
                        "{\"postinumero\": \"00100\", \"paivia\": 2}");
            }
        });

        assertThat(asiakas(PITKA, 3).toimitusaika("00100")).contains(2);
        assertThat(kutsuja).hasValue(3);
    }

    @Test
    void jumittunutPalveluEiJumitaKutsujaa() {
        // Palvelu ottaa pyynnön vastaan mutta ei vastaa koskaan.
        palvelin.createContext("/arviot/", pyynto -> odotaTestinLoppuun());
        var asiakas = asiakas(Duration.ofMillis(300), 2);

        // Kaksi yritystä ja viive: sekunnin luokkaa, ei ikuisuutta.
        var arvio = assertTimeout(Duration.ofSeconds(20),
                () -> asiakas.toimitusaika("00100"));
        assertThat(arvio).isEmpty();
    }

    @Test
    void asiakkaanVirhettaEiToisteta() {
        palvelin.createContext("/arviot/", pyynto -> {
            kutsuja.incrementAndGet();
            vastaa(pyynto, 404, "");
        });

        assertThatThrownBy(() -> asiakas(PITKA, 3).toimitusaika("x"))
                .isInstanceOf(HttpClientErrorException.NotFound.class);
        assertThat(kutsuja).hasValue(1);
    }
    // @loppu testit

    private ToimitusAsiakas asiakas(Duration vastausraja, int yrityksia) {
        String osoite = "http://127.0.0.1:" + palvelin.getAddress().getPort();
        return new ToimitusAsiakas(osoite, Duration.ofSeconds(5),
                vastausraja, yrityksia, Duration.ofMillis(10));
    }

    private static void vastaa(HttpExchange pyynto, int tila, String runko)
            throws IOException {
        byte[] tavut = runko.getBytes(StandardCharsets.UTF_8);
        pyynto.getResponseHeaders().set("Content-Type", "application/json");
        long pituus = tavut.length == 0 ? -1 : tavut.length;
        pyynto.sendResponseHeaders(tila, pituus);
        try (var ulos = pyynto.getResponseBody()) {
            ulos.write(tavut);
        }
    }

    private void odotaTestinLoppuun() {
        try {
            lopeta.await();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
