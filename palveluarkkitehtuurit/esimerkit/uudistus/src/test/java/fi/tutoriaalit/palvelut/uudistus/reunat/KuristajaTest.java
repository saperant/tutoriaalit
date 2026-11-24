package fi.tutoriaalit.palvelut.uudistus.reunat;

import static org.assertj.core.api.Assertions.assertThat;

import com.sun.net.httpserver.HttpServer;
import fi.tutoriaalit.palvelut.uudistus.Http;
import fi.tutoriaalit.palvelut.uudistus.reunat.Kuristaja.Ero;
import fi.tutoriaalit.palvelut.uudistus.reunat.Kuristaja.Kohde;
import fi.tutoriaalit.palvelut.uudistus.uusi.Laskupalvelu;
import fi.tutoriaalit.palvelut.uudistus.vanha.Asiakasrekisteri;
import java.math.BigDecimal;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class KuristajaTest {
    HttpServer vanha;
    HttpServer uusi;
    final Map<String, List<BigDecimal>> laskut = new ConcurrentHashMap<>();
    Kuristaja kuristaja;

    @BeforeEach
    void kaynnista() {
        vanha = Asiakasrekisteri.kaynnista(Map.of(
                "1001", "1001;VIRTANEN AINO;A;20230115",
                "1002", "1002;KORHONEN EERO;A;20240301"));
        // Uudessa on bugi: asiakkaan 1002 toinen lasku puuttuu.
        laskut.put("1001", List.of(new BigDecimal("100.00"),
                                   new BigDecimal("89.50")));
        laskut.put("1002", List.of(new BigDecimal("100.00")));
        uusi = Laskupalvelu.kaynnista(laskut);
        kuristaja = new Kuristaja(Http.osoite(vanha), Http.osoite(uusi));
    }

    @AfterEach
    void sammuta() {
        kuristaja.sulje();
        uusi.stop(0);
        vanha.stop(0);
    }

    Http.Vastaus hae(String polku) {
        return Http.hae(kuristaja.osoite().resolve(URI.create(polku)));
    }

    /** Kuka vastasi: julkisivu kertoo sen otsakkeessa X-Lahde. */
    String lahde(String polku) throws Exception {
        var pyynto = HttpRequest.newBuilder(
                kuristaja.osoite().resolve(URI.create(polku))).build();
        return HttpClient.newHttpClient()
            .send(pyynto, HttpResponse.BodyHandlers.discarding())
            .headers().firstValue("X-Lahde").orElseThrow();
    }

    // @alku vaiheet
    @Test
    void reittiSiirtyyVaiheittainVanhaltaUudelle() throws Exception {
        // 1. Aluksi kaikki menee vanhalle.
        assertThat(hae("/laskut?nro=1001").runko()).isEqualTo("2;189,50");

        // 2. Rinnakkaisajo: asiakas saa yhä vanhan vastauksen, mutta
        //    uuden vastaukset verrataan ja erot kirjataan.
        kuristaja.ohjaa("/laskut", Kohde.RINNAKKAIN);
        assertThat(hae("/laskut?nro=1001").runko()).isEqualTo("2;189,50");
        assertThat(hae("/laskut?nro=1002").runko()).isEqualTo("2;189,50");
        assertThat(kuristaja.erot()).containsExactly(
                new Ero("/laskut?nro=1002", "2;189,50", "1;100,00"));

        // 3. Bugi korjataan, eikä uusia eroja synny. Reitti siirretään
        //    uudelle; asiakastietojen reitti jää vielä vanhalle.
        laskut.put("1002", List.of(new BigDecimal("100.00"),
                                   new BigDecimal("89.50")));
        kuristaja.ohjaa("/laskut", Kohde.UUSI);
        assertThat(hae("/laskut?nro=1002").runko()).isEqualTo("2;189,50");
        assertThat(lahde("/laskut?nro=1002")).isEqualTo("UUSI");
        assertThat(lahde("/asiakas?nro=1001")).isEqualTo("VANHA");
    }
    // @loppu vaiheet

    @Test
    void uudenKaatuminenEiNayRinnakkaisajossa() {
        kuristaja.ohjaa("/laskut", Kohde.RINNAKKAIN);
        uusi.stop(0);
        assertThat(hae("/laskut?nro=1001").runko()).isEqualTo("2;189,50");
        assertThat(kuristaja.erot()).hasSize(1);
    }
}
