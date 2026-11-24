package fi.tutoriaalit.palveluturva.luottamus;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpsConfigurator;
import com.sun.net.httpserver.HttpsExchange;
import com.sun.net.httpserver.HttpsParameters;
import com.sun.net.httpserver.HttpsServer;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.security.cert.X509Certificate;
import java.util.Optional;
import java.util.concurrent.Executors;
import javax.net.ssl.SSLPeerUnverifiedException;

/**
 * Pieni HTTP- tai HTTPS-palvelin esimerkkeihin (JDK:n HttpServer).
 * mTLS-tilassa palvelin vaatii asiakkaalta varmenteen ja kertoo
 * käsittelijälle kutsujan SPIFFE-tunnisteen.
 */
public final class Palvelin implements AutoCloseable {

    /** Pyyntö käsittelijälle. Kutsuja on tyhjä, jos sitä ei tiedetä. */
    public record Pyynto(Optional<String> kutsuja, String metodi,
                         String polku, HttpExchange vaihto) {
        public String otsake(String nimi) {
            return vaihto.getRequestHeaders().getFirst(nimi);
        }
    }

    public record Vastaus(int tila, String runko) {}

    public interface Kasittelija {
        Vastaus kasittele(Pyynto pyynto);
    }

    private final HttpServer palvelin;
    private final String skeema;

    private Palvelin(HttpServer palvelin, String skeema) {
        this.palvelin = palvelin;
        this.skeema = skeema;
    }

    /** Tavallinen HTTP ilman todennusta kuljetuskerroksessa. */
    public static Palvelin http(Kasittelija kasittelija) {
        try {
            HttpServer p = HttpServer.create(
                    new InetSocketAddress("localhost", 0), 0);
            return kaynnista(new Palvelin(p, "http"), kasittelija);
        } catch (IOException e) {
            throw new IllegalStateException(e);
        }
    }

    // @alku mtls
    /** HTTPS, joka vaatii asiakkaalta varmenteen (mTLS). */
    public static Palvelin mtls(VaihdettavaTls tls,
                                Kasittelija kasittelija) {
        try {
            HttpsServer p = HttpsServer.create(
                    new InetSocketAddress("localhost", 0), 0);
            p.setHttpsConfigurator(new HttpsConfigurator(tls.konteksti()) {
                @Override
                public void configure(HttpsParameters parametrit) {
                    var ssl = getSSLContext().getDefaultSSLParameters();
                    ssl.setNeedClientAuth(true); // ilman varmennetta ei
                    parametrit.setSSLParameters(ssl); // yhteyttä synny
                }
            });
            return kaynnista(new Palvelin(p, "https"), kasittelija);
        } catch (IOException e) {
            throw new IllegalStateException(e);
        }
    }

    /** Kutsujan identiteetti tulee TLS-istunnosta, ei otsakkeesta. */
    static Optional<String> kutsuja(HttpExchange vaihto) {
        if (!(vaihto instanceof HttpsExchange https)) {
            return Optional.empty();
        }
        try {
            var ketju = https.getSSLSession().getPeerCertificates();
            return Identiteetti.spiffeId((X509Certificate) ketju[0]);
        } catch (SSLPeerUnverifiedException e) {
            return Optional.empty();
        }
    }
    // @loppu mtls

    private static Palvelin kaynnista(Palvelin p, Kasittelija k) {
        p.palvelin.setExecutor(Executors.newVirtualThreadPerTaskExecutor());
        p.palvelin.createContext("/", vaihto -> {
            try (vaihto) {
                Vastaus v = k.kasittele(new Pyynto(kutsuja(vaihto),
                        vaihto.getRequestMethod(),
                        vaihto.getRequestURI().getPath(), vaihto));
                byte[] runko = v.runko().getBytes(StandardCharsets.UTF_8);
                vaihto.sendResponseHeaders(v.tila(),
                        runko.length == 0 ? -1 : runko.length);
                vaihto.getResponseBody().write(runko);
            }
        });
        p.palvelin.start();
        return p;
    }

    public URI osoite(String polku) {
        return URI.create(skeema + "://localhost:"
                + palvelin.getAddress().getPort() + polku);
    }

    @Override
    public void close() {
        palvelin.stop(0);
    }
}
