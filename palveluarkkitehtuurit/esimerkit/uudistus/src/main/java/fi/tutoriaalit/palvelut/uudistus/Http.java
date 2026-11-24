package fi.tutoriaalit.palvelut.uudistus;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.Executors;

/** HTTP-apuneuvot: palvelin vapaassa portissa ja yksinkertainen haku. */
public final class Http {
    public record Vastaus(int tila, String tyyppi, String runko) {
    }

    private static final HttpClient ASIAKAS = HttpClient.newHttpClient();

    static {
        System.setProperty("sun.net.httpserver.nodelay", "true");
    }

    private Http() {
    }

    public static HttpServer palvelin(HttpHandler kasittelija) {
        try {
            var http = HttpServer.create(
                    new InetSocketAddress("127.0.0.1", 0), 0);
            http.setExecutor(Executors.newVirtualThreadPerTaskExecutor());
            http.createContext("/", kasittelija);
            http.start();
            return http;
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public static URI osoite(HttpServer palvelin) {
        return URI.create("http://127.0.0.1:"
                + palvelin.getAddress().getPort());
    }

    public static Vastaus hae(URI osoite) {
        try {
            var v = ASIAKAS.send(HttpRequest.newBuilder(osoite).build(),
                    HttpResponse.BodyHandlers.ofString());
            return new Vastaus(v.statusCode(),
                    v.headers().firstValue("Content-Type").orElse(""),
                    v.body());
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException(e);
        }
    }

    public static void vastaa(HttpExchange vaihto, Vastaus vastaus)
            throws IOException {
        byte[] runko = vastaus.runko().getBytes(StandardCharsets.UTF_8);
        vaihto.getResponseHeaders().set("Content-Type", vastaus.tyyppi());
        vaihto.sendResponseHeaders(vastaus.tila(), runko.length);
        try (var ulos = vaihto.getResponseBody()) {
            ulos.write(runko);
        }
    }
}
