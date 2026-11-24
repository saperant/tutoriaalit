package fi.tutoriaalit.palvelut.etakutsut.myynti;

import fi.tutoriaalit.palvelut.etakutsut.kestavyys.Uudelleenyritys;
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import tools.jackson.databind.json.JsonMapper;

/**
 * Myynnin asiakas varastopalvelun saldorajapinnalle. Jokaisella
 * etäkutsulla on aikaraja, ohimenevät virheet yritetään uudelleen, ja
 * katkaisija lopettaa kutsut, kun varasto on selvästi alhaalla.
 */
public final class SaldoAsiakas {
    private static final JsonMapper JSON = new JsonMapper();
    private final HttpClient http = HttpClient.newBuilder()
        .connectTimeout(Duration.ofMillis(500)).build();
    private final URI varasto;
    private final Duration aikaraja;
    private final Uudelleenyritys uudelleen;
    private final CircuitBreaker katkaisija;

    public SaldoAsiakas(URI varasto, Duration aikaraja,
                        Uudelleenyritys uudelleen,
                        CircuitBreaker katkaisija) {
        this.varasto = varasto;
        this.aikaraja = aikaraja;
        this.uudelleen = uudelleen;
        this.katkaisija = katkaisija;
    }

    // @alku saldo
    public int saldo(String tuote) {
        // Uudelleenyritys uloimpana: jokainen yritys kulkee katkaisijan
        // läpi, ja avoin katkaisija (CallNotPermittedException) ei ole
        // ohimenevä virhe, joten sitä ei yritetä uudelleen.
        return uudelleen.aja(
            () -> katkaisija.executeSupplier(() -> haeKerran(tuote)),
            e -> e instanceof PalveluEiVastaa);
    }

    private int haeKerran(String tuote) {
        var pyynto = HttpRequest.newBuilder(
                    varasto.resolve("/saldo/" + tuote))
                .timeout(aikaraja).GET().build();
        HttpResponse<String> vastaus;
        try {
            vastaus = http.send(pyynto,
                    HttpResponse.BodyHandlers.ofString());
        } catch (IOException e) {
            throw new PalveluEiVastaa("varasto ei vastaa", e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new PalveluEiVastaa("keskeytetty", e);
        }
        return switch (vastaus.statusCode()) {
            case 200 -> JSON.readTree(vastaus.body()).get("saldo").asInt();
            case 404 -> throw new TuntematonTuote(tuote);
            default -> throw new PalveluEiVastaa(
                    "varasto vastasi " + vastaus.statusCode(), null);
        };
    }
    // @loppu saldo
}
