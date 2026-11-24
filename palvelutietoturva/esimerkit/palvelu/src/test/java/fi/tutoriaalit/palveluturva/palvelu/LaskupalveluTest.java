package fi.tutoriaalit.palveluturva.palvelu;

import static org.assertj.core.api.Assertions.assertThat;

import fi.tutoriaalit.palveluturva.havainnointi.Auditointiloki;
import fi.tutoriaalit.palveluturva.luottamus.Asiakas;
import fi.tutoriaalit.palveluturva.luottamus.Identiteetti;
import fi.tutoriaalit.palveluturva.luottamus.Pem;
import fi.tutoriaalit.palveluturva.luottamus.Varmentaja;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class LaskupalveluTest {

    static final String ALUE = "spiffe://kauppa.example/";
    static final Varmentaja CA = Varmentaja.luo("Kaupan sisäinen CA");
    static final List<java.security.cert.X509Certificate> LUOTETUT =
            List.of(CA.juuri());

    // @alku pem
    @DynamicPropertySource
    static void varmenteet(DynamicPropertyRegistry r) throws IOException {
        Path hak = Files.createTempDirectory("laskutus");
        Identiteetti oma = CA.myonna(ALUE + "laskutus",
                Duration.ofHours(1));
        Pem.kirjoita(oma, hak.resolve("varmenne.pem"),
                hak.resolve("avain.pem"));
        Files.writeString(hak.resolve("juuret.pem"),
                Pem.varmenne(CA.juuri()));
        r.add("PALVELU_VARMENNE", () -> hak.resolve("varmenne.pem")
                .toUri().toString());
        r.add("PALVELU_AVAIN", () -> hak.resolve("avain.pem")
                .toUri().toString());
        r.add("LUOTETUT_JUURET", () -> hak.resolve("juuret.pem")
                .toUri().toString());
    }
    // @loppu pem

    @LocalServerPort
    int portti;

    @Autowired
    Auditointiloki loki;

    Asiakas.Tulos kutsu(String metodi, String palvelu, String polku) {
        var tls = CA.myonna(ALUE + palvelu, Duration.ofMinutes(10))
                .tlsKonteksti(LUOTETUT);
        URI osoite = URI.create("https://localhost:" + portti + polku);
        try (HttpClient http = HttpClient.newBuilder().sslContext(tls)
                .build()) {
            var vastaus = http.send(HttpRequest.newBuilder(osoite)
                    .method(metodi, HttpRequest.BodyPublishers.noBody())
                    .header("X-Korrelaatio", "k-" + palvelu).build(),
                    HttpResponse.BodyHandlers.ofString());
            return new Asiakas.Tulos(vastaus.statusCode(), vastaus.body());
        } catch (IOException e) {
            return new Asiakas.Tulos(0, e.getClass().getSimpleName());
        } catch (InterruptedException e) {
            throw new IllegalStateException(e);
        }
    }

    @Test
    void oikeudetPalvelunIdentiteetinMukaan() {
        // @alku testi
        assertThat(kutsu("GET", "tilaus", "/laskut/7"))
                .hasToString("200 lasku 7: 120,00 €");
        assertThat(kutsu("DELETE", "tilaus", "/laskut/7").tila())
                .isEqualTo(403);          // lukija ei saa mitätöidä
        assertThat(kutsu("DELETE", "hallinta", "/laskut/7"))
                .hasToString("200 lasku 7 mitätöity");
        assertThat(kutsu("GET", "suositukset", "/laskut/7").tila())
                .isEqualTo(403);          // todennettu, ei oikeuksia
        // @loppu testi
        assertThat(loki.rivit()).anySatisfy(rivi -> assertThat(rivi)
                .contains("\"toimija\":\"spiffe://kauppa.example/hallinta\"")
                .contains("\"toiminto\":\"laskut:Mitatoi\""));
    }

    @Test
    void ilmanLuotettuaVarmennettaEiYhteytta() {
        var vieras = Varmentaja.luo("Hyökkääjän CA");
        var tls = vieras.myonna(ALUE + "hallinta", Duration.ofMinutes(10))
                .tlsKonteksti(LUOTETUT);
        var tulos = Asiakas.hae(tls, URI.create("https://localhost:"
                + portti + "/laskut/7"), Map.of());
        assertThat(tulos.toString()).isEqualTo("ei yhteyttä");
    }
}
