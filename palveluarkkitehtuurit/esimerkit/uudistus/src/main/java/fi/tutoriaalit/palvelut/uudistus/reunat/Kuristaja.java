package fi.tutoriaalit.palvelut.uudistus.reunat;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import fi.tutoriaalit.palvelut.uudistus.Http;
import java.io.IOException;
import java.net.URI;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * Kuristajaviikunan (strangler fig) julkisivu. Asiakkaat kutsuvat aina
 * tätä, ja julkisivu päättää polun perusteella, vastaako vanha vai uusi
 * järjestelmä. Reitit siirretään uudelle yksi kerrallaan, ja ne voi
 * palauttaa vanhalle, jos uusi ei toimi.
 */
public final class Kuristaja {
    public enum Kohde { VANHA, UUSI, RINNAKKAIN }

    public record Ero(String polku, String vanha, String uusi) {
    }

    private final URI vanha;
    private final URI uusi;
    private final Map<String, Kohde> reitit = new ConcurrentHashMap<>();
    private final List<Ero> erot = new CopyOnWriteArrayList<>();
    private final HttpServer palvelin;

    public Kuristaja(URI vanha, URI uusi) {
        this.vanha = vanha;
        this.uusi = uusi;
        this.palvelin = Http.palvelin(this::kasittele);
    }

    public URI osoite() {
        return Http.osoite(palvelin);
    }

    public void ohjaa(String polku, Kohde kohde) {
        reitit.put(polku, kohde);
    }

    public List<Ero> erot() {
        return List.copyOf(erot);
    }

    // @alku kasittele
    private void kasittele(HttpExchange vaihto) throws IOException {
        URI pyynto = vaihto.getRequestURI();
        Kohde kohde = reitit.getOrDefault(pyynto.getPath(), Kohde.VANHA);
        Http.Vastaus vastaus = switch (kohde) {
            case VANHA -> Http.hae(vanha.resolve(pyynto));
            case UUSI -> Http.hae(uusi.resolve(pyynto));
            case RINNAKKAIN -> rinnakkain(pyynto);
        };
        vaihto.getResponseHeaders().set("X-Lahde", kohde.name());
        Http.vastaa(vaihto, vastaus);
    }

    /** Rinnakkaisajo: molemmat vastaavat, asiakas saa vanhan
     *  (luotetun) vastauksen, ja erot kirjataan tutkittaviksi. */
    private Http.Vastaus rinnakkain(URI pyynto) {
        Http.Vastaus luotettu = Http.hae(vanha.resolve(pyynto));
        try {
            Http.Vastaus kokeilu = Http.hae(uusi.resolve(pyynto));
            if (!kokeilu.equals(luotettu)) {
                erot.add(new Ero(pyynto.toString(), luotettu.runko(),
                        kokeilu.runko()));
            }
        } catch (RuntimeException e) {
            // Uuden vika ei saa näkyä asiakkaalle.
            erot.add(new Ero(pyynto.toString(), luotettu.runko(),
                    e.toString()));
        }
        return luotettu;
    }
    // @loppu kasittele

    public void sulje() {
        palvelin.stop(0);
    }
}
