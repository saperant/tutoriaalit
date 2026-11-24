package fi.tutoriaalit.http;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.InputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Muistiinpanojen REST-rajapinta pelkällä JDK:lla. Näyttää, mitä
 * kehys tekee puolestamme: reitityksen, metodit, tilakoodit,
 * sisältöneuvottelun ja ehdolliset pyynnöt (ETag).
 */
public final class MuistioPalvelin implements AutoCloseable {

    /** Muistio ja sen versio; versio kasvaa jokaisessa muutoksessa. */
    record Muistio(String teksti, long versio) {
        String etag() {
            return "\"v" + versio + "\"";
        }
    }

    private final Map<String, Muistio> muistiot = new ConcurrentHashMap<>();
    private final AtomicLong seuraavaId = new AtomicLong(1);
    private final HttpServer palvelin;

    public MuistioPalvelin(int portti) throws IOException {
        palvelin = HttpServer.create(
                new InetSocketAddress("127.0.0.1", portti), 0);
        palvelin.createContext("/muistiot", this::kasittele);
    }

    public void kaynnista() {
        palvelin.start();
    }

    public int portti() {
        return palvelin.getAddress().getPort();
    }

    @Override
    public void close() {
        palvelin.stop(0);
    }

    // @alku reititys
    private void kasittele(HttpExchange vaihto) throws IOException {
        try (vaihto) {
            String polku = vaihto.getRequestURI().getPath();
            String[] osat = polku.split("/");
            String metodi = vaihto.getRequestMethod();
            if (osat.length == 2) {             // /muistiot
                switch (metodi) {
                    case "GET" -> listaa(vaihto);
                    case "POST" -> luo(vaihto);
                    default -> eiSallittu(vaihto, "GET, POST");
                }
            } else if (osat.length == 3) {      // /muistiot/{id}
                String id = osat[2];
                switch (metodi) {
                    case "GET" -> hae(vaihto, id);
                    case "PUT" -> korvaa(vaihto, id);
                    case "DELETE" -> poista(vaihto, id);
                    default -> eiSallittu(vaihto, "GET, PUT, DELETE");
                }
            } else {
                vastaa(vaihto, 404, "text/plain", "ei löydy\n");
            }
        }
    }
    // @loppu reititys

    private void listaa(HttpExchange vaihto) throws IOException {
        var rivit = new StringBuilder();
        muistiot.entrySet().stream()
                .sorted(Map.Entry.comparingByKey())
                .forEach(e -> rivit.append(e.getKey()).append(": ")
                        .append(e.getValue().teksti()).append('\n'));
        vastaa(vaihto, 200, "text/plain", rivit.toString());
    }

    // @alku luo
    private void luo(HttpExchange vaihto) throws IOException {
        Optional<String> teksti = lueTeksti(vaihto);
        if (teksti.isEmpty()) {
            return;                       // vastaus on jo lähetetty
        }
        String id = Long.toString(seuraavaId.getAndIncrement());
        Muistio uusi = new Muistio(teksti.get(), 1);
        muistiot.put(id, uusi);
        vaihto.getResponseHeaders().set("Location", "/muistiot/" + id);
        vaihto.getResponseHeaders().set("ETag", uusi.etag());
        vastaa(vaihto, 201, "text/plain", "luotu " + id + "\n");
    }
    // @loppu luo

    // @alku hae
    private void hae(HttpExchange vaihto, String id) throws IOException {
        Muistio m = muistiot.get(id);
        if (m == null) {
            vastaa(vaihto, 404, "text/plain", "ei löydy\n");
            return;
        }
        vaihto.getResponseHeaders().set("ETag", m.etag());
        String ehto = vaihto.getRequestHeaders().getFirst("If-None-Match");
        if (m.etag().equals(ehto)) {
            vastaa(vaihto, 304, null, null);   // asiakkaan kopio kelpaa
            return;
        }
        String hyvaksyy = Optional.ofNullable(
                vaihto.getRequestHeaders().getFirst("Accept")).orElse("*/*");
        if (hyvaksyy.contains("application/json")) {
            vastaa(vaihto, 200, "application/json",
                    "{\"id\":\"" + id + "\",\"teksti\":\""
                            + jsonMerkkijono(m.teksti()) + "\"}");
        } else if (hyvaksyy.contains("text/plain")
                || hyvaksyy.contains("*/*")) {
            vastaa(vaihto, 200, "text/plain", m.teksti() + "\n");
        } else {
            vastaa(vaihto, 406, "text/plain",
                    "tuetut: application/json, text/plain\n");
        }
    }
    // @loppu hae

    // @alku korvaa
    private void korvaa(HttpExchange vaihto, String id) throws IOException {
        Optional<String> teksti = lueTeksti(vaihto);
        if (teksti.isEmpty()) {
            return;
        }
        String ehto = vaihto.getRequestHeaders().getFirst("If-Match");
        // compute tekee tarkistuksen ja päivityksen atomisesti avaimelle.
        var tila = new int[1];
        Muistio tulos = muistiot.compute(id, (avain, vanha) -> {
            if (ehto != null && (vanha == null
                    || !vanha.etag().equals(ehto))) {
                tila[0] = 412;                // joku muutti välissä
                return vanha;
            }
            tila[0] = vanha == null ? 201 : 200;
            long versio = vanha == null ? 1 : vanha.versio() + 1;
            return new Muistio(teksti.get(), versio);
        });
        if (tila[0] == 412) {
            vastaa(vaihto, 412, "text/plain", "versio on muuttunut\n");
            return;
        }
        vaihto.getResponseHeaders().set("ETag", tulos.etag());
        vastaa(vaihto, tila[0], "text/plain", "tallennettu " + id + "\n");
    }
    // @loppu korvaa

    private void poista(HttpExchange vaihto, String id) throws IOException {
        if (muistiot.remove(id) == null) {
            vastaa(vaihto, 404, "text/plain", "ei löydy\n");
        } else {
            vastaa(vaihto, 204, null, null);
        }
    }

    // @alku apurit
    /** Lukee text/plain-rungon tai vastaa 415 ja palauttaa tyhjän. */
    private Optional<String> lueTeksti(HttpExchange vaihto)
            throws IOException {
        String tyyppi = vaihto.getRequestHeaders().getFirst("Content-Type");
        if (tyyppi == null || !tyyppi.startsWith("text/plain")) {
            vastaa(vaihto, 415, "text/plain", "odotettiin text/plain\n");
            return Optional.empty();
        }
        try (InputStream runko = vaihto.getRequestBody()) {
            byte[] tavut = runko.readNBytes(10_000);
            return Optional.of(
                    new String(tavut, StandardCharsets.UTF_8).strip());
        }
    }

    private void eiSallittu(HttpExchange vaihto, String sallitut)
            throws IOException {
        vaihto.getResponseHeaders().set("Allow", sallitut);
        vastaa(vaihto, 405, "text/plain", "metodi ei ole sallittu\n");
    }

    private static void vastaa(HttpExchange vaihto, int tila,
            String tyyppi, String runko) throws IOException {
        if (runko == null) {                  // 204 ja 304: ei runkoa
            vaihto.sendResponseHeaders(tila, -1);
            return;
        }
        byte[] tavut = runko.getBytes(StandardCharsets.UTF_8);
        vaihto.getResponseHeaders().set("Content-Type",
                tyyppi + "; charset=utf-8");
        vaihto.sendResponseHeaders(tila, tavut.length);
        vaihto.getResponseBody().write(tavut);
    }
    // @loppu apurit

    static String jsonMerkkijono(String s) {
        var tulos = new StringBuilder();
        for (char c : s.toCharArray()) {
            switch (c) {
                case '"' -> tulos.append("\\\"");
                case '\\' -> tulos.append("\\\\");
                case '\n' -> tulos.append("\\n");
                default -> {
                    if (c < 0x20) {
                        tulos.append(String.format("\\u%04x", (int) c));
                    } else {
                        tulos.append(c);
                    }
                }
            }
        }
        return tulos.toString();
    }

    public static void main(String[] args) throws IOException {
        var palvelin = new MuistioPalvelin(8080);
        palvelin.kaynnista();
        System.out.println("Kuuntelee: http://127.0.0.1:8080/muistiot");
    }
}
