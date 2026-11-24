package fi.tutoriaalit.palvelut.etakutsut.ketju;

import fi.tutoriaalit.palvelut.etakutsut.Palvelin;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

/**
 * Hajautetun monoliitin tyyppivika: palvelu A kutsuu B:tä, joka kutsuu
 * C:tä ja niin edelleen, ja jokainen odottaa seuraavan vastausta.
 */
public final class Ketju {
    private static final HttpClient HTTP = HttpClient.newHttpClient();

    private Ketju() {
    }

    // @alku ketju
    /** Käynnistää palvelut, joista jokainen tekee työnsä ja kutsuu
     *  sitten seuraavaa. Palauttaa palvelut kutsujärjestyksessä. */
    public static List<Palvelin> rakenna(int pituus, Duration tyo) {
        var palvelut = new ArrayList<Palvelin>();
        URI seuraava = null;
        for (int i = 0; i < pituus; i++) {
            URI kutsuttava = seuraava;
            Palvelin p = Palvelin.kaynnista(vaihto -> {
                nuku(tyo);
                if (kutsuttava != null) {
                    hae(kutsuttava);
                }
                Palvelin.vastaa(vaihto, 200, "{}");
            });
            palvelut.addFirst(p);
            seuraava = p.osoite();
        }
        return palvelut;
    }
    // @loppu ketju

    public static void hae(URI osoite) {
        try {
            HTTP.send(HttpRequest.newBuilder(osoite).build(),
                    HttpResponse.BodyHandlers.discarding());
        } catch (IOException e) {
            throw new IllegalStateException(e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException(e);
        }
    }

    private static void nuku(Duration aika) {
        try {
            Thread.sleep(aika);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
