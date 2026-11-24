package fi.tutoriaalit.palvelut.etakutsut;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.net.InetSocketAddress;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.Executors;

/** Pieni HTTP-palvelin esimerkkien palveluille: JDK:n HttpServer
 *  vapaassa portissa, jokainen pyyntö omassa virtuaalisäikeessään. */
public final class Palvelin implements AutoCloseable {
    static {
        // Ilman tätä Naglen algoritmi ja viivästetty kuittaus lisäävät
        // jokaiseen pieneen vastaukseen kymmeniä millisekunteja.
        System.setProperty("sun.net.httpserver.nodelay", "true");
    }

    private final HttpServer http;

    private Palvelin(HttpServer http) {
        this.http = http;
    }

    public static Palvelin kaynnista(HttpHandler kasittelija) {
        try {
            var http = HttpServer.create(
                    new InetSocketAddress("127.0.0.1", 0), 0);
            http.setExecutor(Executors.newVirtualThreadPerTaskExecutor());
            http.createContext("/", kasittelija);
            http.start();
            return new Palvelin(http);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public URI osoite() {
        return URI.create("http://127.0.0.1:" + http.getAddress().getPort());
    }

    /** Lähettää JSON-vastauksen. */
    public static void vastaa(HttpExchange vaihto, int tila, String json)
            throws IOException {
        byte[] runko = json.getBytes(StandardCharsets.UTF_8);
        vaihto.getResponseHeaders().set("Content-Type", "application/json");
        int pituus = runko.length == 0 ? -1 : runko.length;
        vaihto.sendResponseHeaders(tila, pituus);
        try (var ulos = vaihto.getResponseBody()) {
            ulos.write(runko);
        }
    }

    public static String runko(HttpExchange vaihto) throws IOException {
        try (var sisaan = vaihto.getRequestBody()) {
            return new String(sisaan.readAllBytes(), StandardCharsets.UTF_8);
        }
    }

    @Override
    public void close() {
        http.stop(0);
    }
}
