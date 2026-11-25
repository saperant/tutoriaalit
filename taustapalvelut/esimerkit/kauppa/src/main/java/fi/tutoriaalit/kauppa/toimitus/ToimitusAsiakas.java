package fi.tutoriaalit.kauppa.toimitus;

import java.net.http.HttpClient;
import java.time.Duration;
import java.util.Optional;
import java.util.concurrent.ThreadLocalRandom;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClient;

// @alku asiakas
/**
 * Toimituspalvelun asiakas. Jokaisella kutsulla on aikarajat, ja
 * tilapäinen virhe yritetään uudelleen kasvavalla viiveellä.
 */
public class ToimitusAsiakas {

    /** Toimituspalvelun vastaus. */
    public record Arvio(String postinumero, int paivia) {
    }

    private final RestClient http;
    private final int yrityksia;
    private final Duration viive;

    public ToimitusAsiakas(String osoite, Duration yhteysraja,
                           Duration vastausraja, int yrityksia,
                           Duration viive) {
        var tehdas = new JdkClientHttpRequestFactory(HttpClient.newBuilder()
                .connectTimeout(yhteysraja).build());
        tehdas.setReadTimeout(vastausraja);
        this.http = RestClient.builder()
                .baseUrl(osoite).requestFactory(tehdas).build();
        this.yrityksia = yrityksia;
        this.viive = viive;
    }

    /**
     * Arvio toimitusajasta päivinä. Tyhjä, jos palvelu ei vastaa
     * ajoissa: kutsuja näyttää sivun ilman arviota.
     *
     * @throws org.springframework.web.client.HttpClientErrorException
     *         jos pyyntö on virheellinen (4xx); toisto ei auttaisi
     */
    public Optional<Integer> toimitusaika(String postinumero) {
        for (int yritys = 1; ; yritys++) {
            try {
                Arvio arvio = http.get()
                        .uri("/arviot/{postinumero}", postinumero)
                        .retrieve().body(Arvio.class);
                return Optional.of(arvio.paivia());
            } catch (HttpServerErrorException | ResourceAccessException e) {
                // 5xx, aikarajan ylitys tai yhteysvirhe: GET on
                // idempotentti, joten sen voi lähettää uudelleen.
                if (yritys == yrityksia) {
                    return Optional.empty();
                }
                odota(yritys);
            }
        }
    }

    /** Viive kaksinkertaistuu joka yrityksellä; satunnaisuus hajauttaa. */
    private void odota(int yritys) {
        long katto = viive.toMillis() << (yritys - 1);
        try {
            Thread.sleep(ThreadLocalRandom.current().nextLong(katto + 1));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
// @loppu asiakas
